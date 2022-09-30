class MTDStatistics:
    def __init__(self):
        self.mtd_operation_record = []
        self.total_suspended = 0
        self.total_triggered = 0
        self.total_executed = 0
        self.total_attack_interrupted = 0
        self.switch_mtd_interval_at = {}
        self.switch_mtd_strategy_at = {}

    def append_mtd_operation_record(self, mtd_strategy, start_time, finish_time, duration):
        self.mtd_operation_record.append({
            'name': mtd_strategy.name,
            'start_time': start_time,
            'finish_time': finish_time,
            'duration': duration,
            'executed_at': mtd_strategy.resource_type
        })
        self.total_executed += 1

    def append_mtd_interval_record(self, timestamp, mtd_interval):
        self.switch_mtd_interval_at[timestamp] = mtd_interval

    def append_mtd_strategy_record(self, timestamp, mtd_strategy):
        self.switch_mtd_strategy_at[timestamp] = mtd_strategy

    def dict(self):
        return {
            'Total suspended MTD': self.total_suspended,
            'Total triggered MTD': self.total_triggered,
            'Total executed MTD': self.total_executed,
            'Total attack interrupted': self.total_attack_interrupted,
            'Switch MTD interval at': self.switch_mtd_interval_at,
            'Switch MTD strategy at': self.switch_mtd_strategy_at
        }

    def append_total_attack_interrupted(self):
        self.total_attack_interrupted += 1

    def append_total_suspended(self):
        self.total_suspended += 1

    def append_total_triggered(self):
        self.total_triggered += 1

    def get_record(self):
        return self.mtd_operation_record
