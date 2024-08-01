class AbstractBook(object):
    """
        抽象书籍类，定义了书籍的基本属性和通用方法，作为其他具体书籍类的基类。

        属性：
        - character (str): 书籍字符，可能代表书籍的关键标识符、缩略名等。
        - label_number (int): 书籍标签号码，通常用于内部索引或分类识别，初始值为-1。
        - origin_file (str): 书籍原始文件名或路径，记录书籍数据来源。
        - filepath (str): 书籍当前存储路径，用于定位实际文件位置。
        - coordinate (Any): 书籍在某个坐标系下的位置信息，如页码坐标、物理坐标等，具体类型取决于应用场景，初始值为None。

        方法（需子类实现）：
        - abstract_method(): 空抽象方法，子类应覆盖实现具体逻辑。

        注意：此为抽象类，不应直接实例化，而应通过继承并实现其抽象方法来创建具体的书籍类。
        """
    def __init__(self) -> None:
        """
        构造函数，初始化抽象书籍对象的属性。
        参数：无
        返回：无
        """
        self.character = ''  # 书籍字符
        self.label_number = -1  # 书籍标签号码
        self.origin_file = ''  # 书籍原始文件名或路径
        self.filepath = ''  # 书籍当前存储路径
        self.coordinate = None  # 书籍坐标信息
