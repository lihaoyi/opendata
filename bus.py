
# Getting Started

# Need to get this key from https://www.mytransport.sg/content/mytransport/home/dataMall.html
key = open("lta-key.txt").read()

import requests

incidents = requests.get(
    'http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents',
    headers = {"AccountKey": key}
).json()

len(incidents)

incidents.keys()

incidents['value']

len(incidents['value'])


# Pagination

incidents2 = requests.get(
    'http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents',
    params = {"$skip": 50},
    headers = {"AccountKey": key}
).json()


stops = requests.get(
    'http://datamall2.mytransport.sg/ltaodataservice/BusStops',
    params = {"$skip": 50},
    headers = {"AccountKey": key}
).json()


stops2 = requests.get(
    'http://datamall2.mytransport.sg/ltaodataservice/BusStops',
    params = {"$skip": 50},
    headers = {"AccountKey": key}
).json()

def fetch(path, **params):
    return requests.get(
        path,
        params = params,
        headers = {"AccountKey": key}
    ).json()


incidents = fetch('http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents')

len(incidents['value'])


def fetch_all(path, **params):
    output = []
    while True:
        fetched = requests.get(
            path,
            params = {**params, "$skip": len(output)},
            headers = {"AccountKey": key}
        ).json()
        if 'value' not in fetched:
            print(fetched)
            raise Exception()
        elif len(fetched['value']) == 0:
            return output
        else:
            print("fetched: ", len(output))
            output.extend(fetched['value'])

all_incidents = fetch_all('http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents')

# Bulk Data Download

all_stops = fetch_all('http://datamall2.mytransport.sg/ltaodataservice/BusStops')

all_stops[0]

all_stops[0]['BusStopCode']

def find_stop(string):
    return [stop for stop in all_stops if string in stop['Description']]



all_services = fetch_all('http://datamall2.mytransport.sg/ltaodataservice/BusServices')

all_services[0]


from collections import Counter

Counter([service['Operator'] for service in all_services])

all_route_stops = fetch_all('http://datamall2.mytransport.sg/ltaodataservice/BusRoutes')


# Bus Timing Indicator

orchard_bus_timings = [
    (service["ServiceNo"], service["NextBus"]['EstimatedArrival'])
    for stop in find_stop("Opp Orchard Stn")
    for service in fetch(
        'http://datamall2.mytransport.sg/ltaodataservice/BusArrival',
        BusStopID = stop["BusStopCode"]
    )["Services"]
]

import datetime
def pretty_time(timestring):
    now = datetime.datetime.now(datetime.timezone.utc)
    if timestring == "":
        return ""
    else:
        parsed = datetime.datetime.strptime(
            timestring[:-6],
            "%Y-%m-%dT%H:%M:%S"
        )
        delta = parsed.replace(tzinfo = datetime.timezone.utc) - now

        return str(int(delta.seconds / 60)) + "min"

[
    (service, pretty_time(timestring))
    for (service, timestring) in orchard_bus_timings
]

find_stop("Kallang Stn")
find_stop("Anglo-Chinese Sch")

# Path Finding

find_stop("Orchard Stn")
# 09022
find_stop("Anglo-Chinese Sch")
# 40069



all_route_stops[0]

all_routes = {}
for route_stop in all_route_stops:
    id = (route_stop["ServiceNo"], route_stop["Direction"])
    if id not in all_routes:
        all_routes[id] = []

    all_routes[id].append(route_stop)

import pprint
pprint.pprint(list(all_routes.keys()))

for k, v in all_routes.items():
    v.sort(key = lambda route_stop: route_stop["StopSequence"])

all_stop_connections = {}
for route in all_routes.values():
    for i in range(len(route)):
        code = route[i]["BusStopCode"]
        if code not in all_stop_connections:
            all_stop_connections[code] = []
        for j in range(i+1, len(route)):
            all_stop_connections[code].append(
                (route[j]["ServiceNo"], route[j]['BusStopCode'])
            )

from queue import Queue
queue = Queue()
queue.put(('09022', None, None))
seen = set()
result = None
while not queue.empty():
    current = queue.get()
    (stop_id, service, parents) = current

    if stop_id == "40069":
        result = current
        break
    if stop_id in seen:
        continue
    seen.add(stop_id)
    for (service, dest_stop) in all_stop_connections[stop_id]:
        queue.put((dest_stop, service, current))


final_route = []
while True:
    stop_id, service, result = result
    if result is None:
        break
    else:
        final_route.append((stop_id, service))

final_route.reverse()

all_stops_by_id = {stop["BusStopCode"]: stop for stop in all_stops}

for stop_id, service in final_route:
    print("Take " + service + " to " + all_stops_by_id[stop_id]["Description"])

find_stop("Boon Lay")
find_stop("Changi Airport")
