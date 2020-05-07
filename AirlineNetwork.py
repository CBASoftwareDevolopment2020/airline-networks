from collections import namedtuple, defaultdict, deque
import heapq
from sys import maxsize
from pprint import pprint as pp
from time import time as seconds

Aircraft = namedtuple('Aircraft', 'CODE NAME CATEGORY')
Airline = namedtuple('Airline', 'CODE NAME COUNTRY')
Airport = namedtuple('Airport', 'CODE NAME CITY COUNTRY LATITUDE LONGITUDE')
Route = namedtuple('Route', 'AIRLINE_CODE SOURCE_CODE DESTINATION_CODE DISTANCE TIME')


def read_aircrafts():
    global Aircraft
    aircrafts = []
    with open('aircrafts.txt', encoding="utf-8") as f:
        for idx, line in enumerate(f.readlines()[1:]):
            cols = line.strip().split(';')
            aircrafts.append(Aircraft(*cols))
    return aircrafts


def read_airlines():
    global Airline
    airlines = []
    with open('airlines.txt', encoding="utf-8") as f:
        for idx, line in enumerate(f.readlines()[1:]):
            cols = [line[:3]] + line[4:].strip().split(';')
            airlines.append(Airline(*cols))
    return airlines


def read_airports():
    global Airport
    airports = []
    with open('airports.txt', encoding="utf-8") as f:
        for idx, line in enumerate(f.readlines()[1:]):
            cols = line.strip().split(';')
            airports.append(Airport(*cols))
    return airports


def read_routes():
    global Route
    routes = []
    with open('routes.txt', encoding="utf-8") as f:
        for idx, line in enumerate(f.readlines()[1:]):
            cols = line.strip().split(';')
            routes.append(Route(*cols))
    return routes


def read_data():
    return read_aircrafts(), read_airlines(), read_airports(), read_routes()


class AirlineNetwork(object):
    __slots__ = ['_num_airports', '_num_routes', '_airports', '_airlines']

    def __init__(self, airports: iter, routes: iter, airlines: iter):
        self._num_airports = 0
        self._num_routes = 0
        self._airports = defaultdict(dict)
        self._airlines = airlines

        for vertex in airports:
            self.add_vertex(vertex)

        for edge in routes:
            self.add_edge(edge)

        # pp(self._vertices)

    @property
    def num_vertices(self):
        return self._num_airports

    @property
    def num_edges(self):
        return self._num_routes

    def add_vertex(self, vertex: Airport):
        code, name, city, country, latitude, longitude = vertex
        self._airports[code] = {'name': name, 'city': city, 'country': country, 'latitude': float(latitude),
                                'longitude': float(longitude), 'routes': []}
        self._num_airports += 1

    def add_edge(self, edge: Route):
        airline_code, source_code, destination_code, distance, time = edge
        self._airports[source_code]['routes'].append(
            {'airline': airline_code, 'from': source_code, 'to': destination_code, 'distance': float(distance),
             'time': float(time)})
        self._num_routes += 1

    def is_connected_df(self, start: str, end: str, airline: str):
        stack = deque()
        visited = []
        stack.extend([route for route in self._airports[start]['routes'] if route['airline'] == airline])
        while len(stack) > 0:
            cur = stack.pop()
            if any(x for x in visited if x == cur):
                continue
            visited.append(cur)
            if cur['to'] == end:
                return True

            next = [route for route in self._airports[cur['to']]['routes'] if route['airline'] == airline]
            stack.extend(next)

        return False

    def is_connected_bf(self, start: str, end: str, airline: str):
        stack = deque()
        visited = []
        stack.extend([route for route in self._airports[start]['routes'] if route['airline'] == airline])
        while len(stack) > 0:
            cur = stack.popleft()
            if any(x for x in visited if x == cur):
                continue
            visited.append(cur)
            if cur['to'] == end:
                return True

            next = [route for route in self._airports[cur['to']]['routes'] if route['airline'] == airline]
            stack.extend(next)

        return False

    def shortes_route_distance(self, start: str, end: str):
        pq = []
        dist_to = {}
        visited = []

        for key, value in self._airports.items():
            dist_to[key] = (maxsize, None)
        dist_to[start] = (0, None)
        pq.append((start, 0))
        while len(pq) > 0:
            pq = sorted(pq, key=lambda x: x[1])
            cur = pq.pop(0)
            if cur[0] in visited:
                continue
            visited.append(cur[0])
            for route in self._airports[cur[0]]['routes']:
                if dist_to[route['to']][0] > dist_to[cur[0]][0] + route['distance']:
                    dist_to[route['to']] = (dist_to[cur[0]][0] + route['distance'], route['from'])
                for x in pq:
                    if route['to'] in x:
                        x = (route['to'], dist_to[route['to']][0])
                else:
                    if route['to'] not in visited:
                        pq.append((route['to'], dist_to[route['to']][0]))
        return self._get_shortest_path(end, dist_to), dist_to[end][0]

    def shortes_route_time(self, start: str, end: str):
        pq = []
        dist_to = {}
        visited = []

        for key, value in self._airports.items():
            dist_to[key] = (maxsize, None)
        dist_to[start] = (0, None)
        pq.append((start, 0))
        while len(pq) > 0:
            pq = sorted(pq, key=lambda x: x[1])
            cur = pq.pop(0)
            if cur[0] in visited:
                continue
            visited.append(cur[0])
            for route in self._airports[cur[0]]['routes']:
                if dist_to[route['to']][0] > dist_to[cur[0]][0] + route['time']:
                    dist_to[route['to']] = (dist_to[cur[0]][0] + route['time'], route['from'])
                for x in pq:
                    if route['to'] in x:
                        x = (route['to'], dist_to[route['to']][0])
                else:
                    if route['to'] not in visited:
                        pq.append((route['to'], dist_to[route['to']][0]))
        return self._get_shortest_path(end, dist_to), dist_to[end][0]

    def widest_coverage(self):
        pass

    def _get_shortest_path(self, end: str, dist_to: dict) -> str:
        if end:
            cur = self._get_shortest_path(dist_to[end][1], dist_to)
            res = f'{f"{cur} -> " if cur else ""}{end}'
            return res
        else:
            return ''


if __name__ == '__main__':
    aircrafts, airlines, airports, routes = read_data()

    start = seconds()
    network = AirlineNetwork(airports, routes, airlines)
    end = seconds()
    print('network', end - start)

    start = seconds()
    print(network.is_connected_df('CPH', 'LGW', 'U2'))
    print(network.is_connected_df('CPH', 'LGW', 'DX'))
    end = seconds()
    print('df', end - start)

    start = seconds()
    print(network.is_connected_bf('CPH', 'LGW', 'U2'))
    print(network.is_connected_bf('CPH', 'LGW', 'DX'))
    end = seconds()
    print('bf', end - start)

    start = seconds()
    print(network.shortes_route_distance('CPH', 'LGW'))
    end = seconds()
    print('sp_dis', end - start)
    start = seconds()
    print(network.shortes_route_time('CPH', 'LGW'))
    end = seconds()
    print('sp_time', end - start)

    # print(f'{"Expected".ljust(10)}: Airports: {len(airports)}, Routes: {len(routes)}')
    # print(f'{"Actual".ljust(10)}: Airports: {network.num_vertices}, Routes: {network.num_edges}')
