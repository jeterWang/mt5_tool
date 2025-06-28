class BaseCommand:
    """
    命令模式基类，所有具体命令需实现execute方法。
    """

    def execute(self):
        raise NotImplementedError("子类必须实现execute方法")

    def undo(self):
        """
        可选：如需支持撤销操作，子类可实现undo方法。
        """
        pass
