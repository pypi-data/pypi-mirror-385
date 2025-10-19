import json
import os
import time
from collections import defaultdict

import cv2
from loguru import logger
import uiautomator2 as ui2
from rapidocr_onnxruntime import RapidOCR, VisRes


class HDevice(ui2.Device):
    debug: bool = False

    def __init__(
            self, device_serial: str, text_score: float = 0.7, debug: bool = False
    ):
        """
        :param device_serial: 设备名或者Wi-Fi连接的地址（需要附带端口）
        :param text_score: ocr 识别的相似度控制
        :param debug: debug模式
        """
        self.engine = RapidOCR(text_score=text_score)
        if debug:
            self.debug = debug
            logger.debug("调试模式已启用")
            self.vis = VisRes()
        super().__init__(device_serial)

    def click_text_by_ocr(self, text, index: int = 0):
        """
        通过ocr点击文字/按钮等
        :param text:
        :param index: 屏幕中存在相同多个文字时，可以控制索引
        :return:
        """
        logger.debug(f"通过文本查找并点击: '{text}' (索引: {index})")
        format_text = (
            text.lower().replace(" ", "").strip()
        )  # 统一转小写，并删除空格 减少容错
        try:
            results, image_path, _ = self.ocr_get_text_from_image()
            if not results:
                logger.warning(f"OCR识别结果为空，无法点击文本: '{format_text}'")
                return False

            current_dict = defaultdict(list)
            [
                current_dict[result[1].strip()].append({"coord": result[0]})
                for result in results or []
                if result[1].strip()
            ]

            target_info = current_dict.get(format_text)
            if not target_info:
                logger.warning(f"未找到文本: '{text}'")
                return False

            try:
                target_info = target_info[index]
            except IndexError:
                logger.error(f"索引超出范围: {index}，可用索引数量: {len(target_info)}")
                return False

            coord_data = target_info.get("coord")
            if not coord_data:
                logger.error(f"坐标数据为空: {target_info}")
                return False

            target_coord_x, target_coord_y = self.calculate_center_point(coord_data)

            self.click(target_coord_x, target_coord_y)
            logger.debug(f"成功点击: ({target_coord_x}, {target_coord_y})")
            return True

        except Exception as e:
            logger.error(f"通过文本点击时发生错误: {e}")
            return False

    @staticmethod
    def calculate_center_point(coord: list):
        """
        计算物体中心坐标
        :param coord: (x,y)
        :return:
        """
        x = round((coord[2][0] + coord[3][0]) / 2, 0)
        y = round((coord[0][1] + coord[3][1]) / 2, 0)
        logger.debug(f"计算中心点: {coord} -> ({x}, {y})")
        return x, y

    def ocr_get_text_from_image(self):
        """"""
        image_path = f"./{int(time.time())}.png"
        try:
            self.screenshot(image_path)
            results, _ = self.engine(
                image_path, use_det=True, use_cls=True, use_rec=True
            )

            # TODO 这里做了一个异常修复，不是很完美
            fix_results = []
            for result in results:
                text = result[1].strip().lower().replace(" ", "")
                result[1] = text
                fix_results.append(result)

            # 调试模式下保存带标注的图片
            if self.debug and fix_results:
                debug_image = cv2.imread(image_path)
                boxes, _, scores = list(zip(*fix_results))
                res = self.vis(debug_image, boxes)
                debug_image_path = f"./vis_cache/only_vis_det_{int(time.time())}.png"
                debug_content_path = f"./vis_cache/only_vis_det_{int(time.time())}.txt"
                os.makedirs("./vis_cache", exist_ok=True)
                cv2.imwrite(debug_image_path, res)
                logger.debug(f"调试图片保存到: {debug_image_path}")
                with open(debug_content_path, "w") as file:
                    file.write(json.dumps(fix_results, indent=4, ensure_ascii=False))
                logger.debug(f"调试文本保存到: {debug_content_path}")

            # 删除临时截图
            if os.path.exists(image_path):
                os.remove(image_path)
            json_result = json.dumps(results, ensure_ascii=False) if results else ""
            return results, image_path, json_result

        except Exception as e:
            logger.error(f"截图和文字提取时发生错误: {e}")
            # 确保临时文件被清理
            if os.path.exists(image_path):
                os.remove(image_path)
            return None, image_path, ""

    def wait_text_by_ocr(self, text: str, timeout: int = 1):
        """
        等待某个关键词是否出现 通过RapidOCR实现
        :param text:
        :param timeout:
        :return:
        """
        start_timestamp = time.time()
        format_text = (
            text.lower().replace(" ", "").strip()
        )  # TODO 统一转小写，并删除空格
        while time.time() - start_timestamp < timeout:
            try:
                _, _, ocr_result = self.ocr_get_text_from_image()
                if format_text in ocr_result:
                    logger.debug(f"找到文本: '{text}'")
                    return True
            except Exception as e:
                logger.error(f"图片文本识别时发生错误: {e}")
        logger.warning(f"未在图片中找到文本: '{text}'")
        return False

    def wait_text_by_hierarchy(
            self, text: str, stop_text: str = None, timeout: int = 10
    ):
        """
        等待某个关键词是否出现 通过dump_hierarchy实现
        :param text: 要等待的文本
        :param timeout: 超时时间（秒）
        :param stop_text: 停止条件文本，如果找到该文本则停止等待
        :return: True表示找到目标文本，False表示超时或找到停止条件
        """
        start_timestamp = time.time()
        while time.time() - start_timestamp < timeout:
            hierarchy = self.dump_hierarchy()

            # 检查是否找到停止条件文本
            if stop_text and stop_text in hierarchy:
                return False  # 找到停止条件，返回False

            # 检查是否找到目标文本
            if text in hierarchy:
                return True  # 找到目标文本，返回True

            time.sleep(1)

        return False  # 超时返回False

    def input_text_by_adb(self, text: str, max_char: int = 2):
        """
        通过adb shell 输入文字
        :param text:
        :param max_char: 单词输入字符数量
        :return:
        """
        if not text:
            return
        logger.debug(f"输入文本: {text}")
        try:
            # 每次最多处理4个字符
            for i in range(0, len(text), max_char):
                chunk = text[i: i + max_char]
                # 使用 shlex.quote 安全转义，防止 shell 特殊字符导致命令错误
                self.shell(f"input text {chunk}")
        except Exception as e:
            logger.error(f"输入文本时发生错误: {e}")
            raise
