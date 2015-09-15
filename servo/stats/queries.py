# -*- coding: utf-8 -*-

import decimal
from django.db import connection


class StatsManager:
    def __init__(self):
        self.cursor = connection.cursor()

    def _result(self, args):
        result = []
        self.cursor.execute(self.sql, args)
        for k, v in self.cursor.fetchall():
            if isinstance(v, decimal.Decimal):
                v = float(v)
            result.append((k, v,))

        return result

    def cases_per_tech(self, location, queues, labels, start, end):
        users = User.object.filter(location=location)


    def statuses_per_location(self, timescale, location, status, start, end):
        self.sql = """SELECT EXTRACT(EPOCH FROM date_trunc(%s, se.triggered_at))*1000 as p,
        COUNT(*) AS v
        FROM servo_order so, servo_event se
            WHERE (se.triggered_at, se.triggered_at) OVERLAPS (%s, %s)
            AND se.action = 'set_status'
            AND se.object_id = so.id
            AND so.location_id = %s
            AND se.description = %s
        GROUP BY p
        ORDER BY p ASC"""

        return self._result([timescale, start, end, location, status])

    def statuses_per_user(self, timescale, user, status, start, end):
        self.sql = """SELECT EXTRACT(EPOCH FROM date_trunc(%s, se.triggered_at))*1000 as p,
        COUNT(*) AS v
        FROM servo_order so, servo_event se
            WHERE (se.triggered_at, se.triggered_at) OVERLAPS (%s, %s)
            AND se.action = 'set_status'
            AND se.object_id = so.id
            AND so.user_id = %s
            AND se.description = %s
        GROUP BY p
        ORDER BY p ASC"""

        return self._result([timescale, start, end, user, status])

    def sales_invoices(self, timescale, queue, start, end):
        self.sql = """SELECT EXTRACT(EPOCH FROM date_trunc(%s, so.created_at))*1000 as p,
        SUM(total_gross) AS v
        FROM servo_invoice si, servo_order so
            WHERE (si.created_at, si.created_at) OVERLAPS (%s, %s)
            AND si.order_id = so.id
            AND so.queue_id = %s
        GROUP BY p
        ORDER BY p ASC"""

        return self._result([timescale, start, end, queue])

    def sales_purchases(self, timescale, queue, start, end):
        self.sql = """SELECT EXTRACT(EPOCH FROM date_trunc(%s, po.created_at))*1000 as p,
        SUM(total) AS v
        FROM servo_purchaseorder po, servo_order so
            WHERE (po.created_at, po.created_at) OVERLAPS (%s, %s)
            AND po.sales_order_id = so.id
            AND so.queue_id = %s
        GROUP BY p
        ORDER BY p ASC"""

        return self._result([timescale, start, end, queue])

    def sales_parts_per_labtier(self, start, end):
        self.sql = """SELECT labour_tier, count(*)
        FROM servo_product p, servo_servicepart sp, servo_serviceorderitem soi
        WHERE soi.product_id = p.id
            AND sp.order_item_id = soi.id
            AND (soi.created_at, soi.created_at) OVERLAPS (%s, %s)
            AND char_length(labour_tier) = 4
            GROUP BY labour_tier
            ORDER BY labour_tier"""

        return self._result([start, end])

    def order_runrate(self, timescale, location, user, start, end):
        self.sql = """SELECT EXTRACT(EPOCH FROM date_trunc(%s, started_at))*1000 as p,
        COUNT(*) AS v
        FROM servo_order
        WHERE user_id = %s
            AND location_id = %s
            AND (started_at, started_at) OVERLAPS (%s, %s)
        GROUP BY p
        ORDER BY p ASC"""

        return self._result([timescale, user, location, start, end])

    def turnaround_per_location(self, timescale, location, start, end):
        self.sql = """SELECT EXTRACT(EPOCH FROM date_trunc(%s, created_at))*1000 as p,
            EXTRACT(HOUR FROM AVG(closed_at - created_at)) as v
        FROM servo_order
        WHERE closed_at IS NOT NULL
            AND location_id = %s
            AND queue_id IS NOT NULL
            AND (created_at, created_at) OVERLAPS (%s, %s)
        GROUP BY p
        ORDER BY p ASC"""

        return self._result([timescale, location, start, end])

    def runrate_per_location(self, timescale, location, start, end):
        self.sql = """SELECT EXTRACT(EPOCH FROM date_trunc(%s, created_at))*1000 as p,
        COUNT(*) AS v
        FROM servo_order
        WHERE location_id = %s
            AND closed_at IS NOT NULL
            AND (created_at, created_at) OVERLAPS (%s, %s)
        GROUP BY p
        ORDER BY p ASC"""

        return self._result([timescale, location, start, end])

    def distribution_per_location(self, start, end):
        result = []
        self.sql = """SELECT l.title, COUNT(*)
        FROM servo_order o LEFT OUTER JOIN servo_location l on (o.location_id = l.id)
        WHERE (o.created_at, o.created_at) OVERLAPS (%s, %s)
        GROUP BY l.title"""
        self.cursor.execute(self.sql, [start, end])

        for k, v in self.cursor.fetchall():
            result.append({'label': k, 'data': v})

        return result

    def orders_created_by(self, timescale, location, user, start, end):
        self.sql = """SELECT EXTRACT(EPOCH FROM date_trunc(%s, created_at))*1000 as p,
        COUNT(*) AS v
        FROM servo_order
        WHERE location_id = %s
            AND created_by_id = %s
            AND (created_at, created_at) OVERLAPS (%s, %s)
        GROUP BY p
        ORDER BY p ASC"""

        return self._result([timescale, location, user, start, end])

    def orders_created_at(self, timescale, location, start, end):
        self.sql = """SELECT EXTRACT(EPOCH FROM date_trunc(%s, created_at))*1000 as p,
        COUNT(*) AS v
        FROM servo_order
        WHERE location_id = %s
            AND (created_at, created_at) OVERLAPS (%s, %s)
        GROUP BY p
        ORDER BY p ASC"""

        return self._result([timescale, location, start, end])

    def orders_closed_at(self, timescale, location, start, end):
        self.sql = """SELECT EXTRACT(EPOCH FROM date_trunc(%s, created_at))*1000 as p,
        COUNT(*) AS v
        FROM servo_order
        WHERE location_id = %s
            AND (closed_at, closed_at) OVERLAPS (%s, %s)
        GROUP BY p
        ORDER BY p ASC"""

        return self._result([timescale, location, start, end])

    def orders_closed_in(self, timescale, location, queue, start, end):
        self.sql = """SELECT EXTRACT(EPOCH FROM date_trunc(%s, created_at))*1000 as p,
        COUNT(*) AS v
        FROM servo_order
        WHERE location_id = %s
            AND queue_id = %s
            AND (closed_at, closed_at) OVERLAPS (%s, %s)
        GROUP BY p
        ORDER BY p ASC"""

        return self._result([timescale, location, queue, start, end])
    
    def order_count(self, timescale, location, queue, start, end):
        self.sql = """SELECT EXTRACT(EPOCH FROM date_trunc(%s, created_at))*1000 as p,
        COUNT(*) AS v
        FROM servo_order
        WHERE location_id = %s
            AND queue_id = %s
            AND (created_at, created_at) OVERLAPS (%s, %s)
        GROUP BY p
        ORDER BY p ASC"""

        return self._result([timescale, location, queue, start, end])

    def order_turnaround(self, timescale, location, queue, start, end):
        self.sql = """SELECT EXTRACT(EPOCH FROM date_trunc(%s, created_at))*1000 as p,
            EXTRACT(HOUR FROM AVG(closed_at - created_at)) as v
        FROM servo_order
        WHERE closed_at IS NOT NULL
            AND location_id = %s
            AND queue_id = %s
            AND queue_id IS NOT NULL
            AND (created_at, created_at) OVERLAPS (%s, %s)
        GROUP BY p
        ORDER BY p ASC"""

        return self._result([timescale, location, queue, start, end])

    def order_turnaround(self, timescale, location, queue, start, end):
        self.sql = """SELECT EXTRACT(EPOCH FROM date_trunc(%s, created_at))*1000 as p,
            EXTRACT(HOUR FROM AVG(closed_at - created_at)) as v
        FROM servo_order
        WHERE closed_at IS NOT NULL
            AND location_id = %s
            AND queue_id = %s
            AND queue_id IS NOT NULL
            AND (created_at, created_at) OVERLAPS (%s, %s)
        GROUP BY p
        ORDER BY p ASC"""

        return self._result([timescale, location, queue, start, end])
