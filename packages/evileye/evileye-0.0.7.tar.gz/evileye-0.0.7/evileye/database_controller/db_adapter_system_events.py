import time
from .db_adapter import DatabaseAdapterBase
from psycopg2 import sql
from ..utils import threading_events


class DatabaseAdapterSystemEvents(DatabaseAdapterBase):
    def __init__(self, db_controller):
        super().__init__(db_controller)

    def set_params_impl(self):
        super().set_params_impl()
        self.event_name = 'SystemEvent'

    def _insert_impl(self, event):
        fields, data = self._prepare_for_saving(event)
        insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(self.table_name),
            sql.SQL(",").join(map(sql.Identifier, fields)),
            sql.SQL(', ').join(sql.Placeholder() * len(fields))
        )
        self.queue_in.put((insert_query, data))

    def _update_impl(self, event):
        # No updates for system events
        pass

    def _execute_query(self):
        while self.run_flag:
            time.sleep(0.01)
            try:
                if not self.queue_in.empty():
                    query_string, data = self.queue_in.get()
                    if query_string is not None:
                        pass
                else:
                    query_string = data = None
            except ValueError:
                break

            if query_string is None:
                continue

            self.db_controller.query(query_string, data)
            threading_events.notify('new event')

    def _prepare_for_saving(self, event) -> tuple[list, list]:
        fields_for_saving = {
            'event_id': event.event_id,
            'time_stamp': event.timestamp,
            'event_type': event.event_type,
            'project_id': self.db_controller.get_project_id(),
            'job_id': self.db_controller.get_job_id()
        }
        return list(fields_for_saving.keys()), list(fields_for_saving.values())


