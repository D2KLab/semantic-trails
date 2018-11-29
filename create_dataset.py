import csv
from datetime import timedelta

import ciso8601
import numpy as np
import reverse_geocoder as rg
from haversine import haversine

f_out = "dataset.csv"
f_venues = "venues.csv"
f_checkins = "checkins.csv"

# load the venues
venues = {}
venues_list = []

with open(f_venues, encoding='utf-8') as fp:
    reader = csv.reader(fp, delimiter='\t')

    for row in reader:
        venue_id = row[0]
        venue_lat = float(row[1])
        venue_lon = float(row[2])
        venue_cat = row[3]

        venues_list.append(venue_id)
        venues[venue_id] = {'id': venue_id,
                            'lat': venue_lat,
                            'lon': venue_lon,
                            'cat': venue_cat}

venues_set = set(venues_list)
assert len(list(venues_set)) == len(venues_list)
print("Loading", len(venues), "venues...")

# reverse geocode the cities
coords = []

for venue_id in venues_list:
    venue_lat = venues[venue_id]['lat']
    venue_lon = venues[venue_id]['lon']
    coords.append((venue_lat, venue_lon))

venues_rg = rg.search(coords)

for index, venue_id in enumerate(venues_list):
    venues[venue_id]['city'] = venues_rg[index]['name']
    venues[venue_id]['cc'] = venues_rg[index]['cc']

assert len(venues_rg) == len(venues)
print("Geocoding", len(venues_rg), "venues...")

# load the checkins
checkins = []

months = {'Jan': '01',
          'Feb': '02',
          'Mar': '03',
          'Apr': '04',
          'May': '05',
          'Jun': '06',
          'Jul': '07',
          'Aug': '08',
          'Sep': '09',
          'Oct': '10',
          'Nov': '11',
          'Dec': '12'}


def normalize_datetime(datetime):
    if not datetime[:1].isalpha():
        return datetime

    fields = datetime.split(' ')

    return fields[5] + '-' + months[fields[1]] + '-' + fields[2] + ' ' + fields[3]


def normalize_offset(offset):
    int_offset = int(offset)

    if int_offset < 0:
        sign_offset = "-"
        int_offset *= -1
    else:
        sign_offset = "+"
    
    hour_offset = int_offset // 60
    minute_offset = int_offset % 60

    return sign_offset + str(hour_offset).zfill(2) + str(minute_offset).zfill(2)


with open(f_checkins, encoding='utf-8') as fp:
    reader = csv.reader(fp, delimiter='\t')

    for row in reader:
        try:
            checkin_user = row[0]
            checkin_venue = row[1]
            checkin_datetime = normalize_datetime(row[2])
            checkin_offset = normalize_offset(row[3])

            checkin_timestamp = ciso8601.parse_datetime(checkin_datetime + checkin_offset)

            assert checkin_venue in venues_set

            checkins.append({'user': checkin_user,
                             'venue': checkin_venue,
                             'timestamp': checkin_timestamp})

        except (ValueError, OverflowError, AssertionError, IndexError) as e:
            print(row)

print("Loading", len(checkins), "checkins...")

# sort checkins by user and timestamp
sorted_checkins = sorted(checkins, key=lambda x: (x['user'], x['timestamp']))

fp_out = open(f_out, 'w', encoding='utf8')

sequence_counter = 0
user_counter = 0
users_out = {}

checkins_per_path = []
checkin_counter = None

timedelta_per_path = []
initial_timestamp = None
last_timestamp = None


def save_checkin(checkin, new_path=False):
    global sequence_counter
    global user_counter

    global checkin_counter
    global initial_timestamp
    global last_timestamp

    if new_path:
        # sequence index
        sequence_counter += 1
        # count the checkins per path
        if checkin_counter is not None:
            checkins_per_path.append(checkin_counter)
        checkin_counter = 0
        # compute the duration of each path
        if initial_timestamp is not None:
            timedelta_per_path.append(last_timestamp - initial_timestamp)
        initial_timestamp = int(checkin['timestamp'].timestamp())

    checkin_counter += 1
    last_timestamp = int(checkin['timestamp'].timestamp())

    # user index
    if checkin['user'] not in users_out:
        user_counter += 1
        users_out[checkin['user']] = user_counter

    line = ''
    line += str(sequence_counter) + '\t'
    line += str(users_out[checkin['user']]) + '\t'
    line += str(checkin['venue']) + '\t'
    line += str(venues[checkin['venue']]['cat']) + '\t'
    line += str(venues[checkin['venue']]['city']) + '\t'
    line += str(venues[checkin['venue']]['cc']) + '\t'
    line += checkin['timestamp'].replace(second=0).isoformat() + '\n'
    fp_out.write(line)


def invalid_speed(last_checkin, current_checkin):
    # compute travel duration in seconds
    last_timestamp = int(last_checkin['timestamp'].timestamp())
    current_timestamp = int(current_checkin['timestamp'].timestamp())
    dt = current_timestamp - last_timestamp

    # compute travel distance in metres
    last_venue = last_checkin['venue']
    current_venue = current_checkin['venue']
    ds = abs(haversine((venues[last_venue]['lat'], venues[last_venue]['lon']),
                       (venues[current_venue]['lat'], venues[current_venue]['lon']))) * 1000

    if dt <= 0:
        return True

    # compute speed in m/s
    speed = ds / float(dt)

    # if the speed is too high
    if speed > 331.6:
        return True

    return False


num_checkin = 0
tot_checkins = len(sorted_checkins)

num_same_venue = 0
num_invalid_time = 0
num_invalid_speed = 0

last_user = None
last_checkin = None
current_path = []

# create the paths
for current_checkin in sorted_checkins:
    # count the checkins
    num_checkin = num_checkin + 1
    if num_checkin % 10000 == 0:
        print("Processing checkin", num_checkin, "of", tot_checkins)

    # check if the user is new
    if last_user != current_checkin['user']:
        last_user = current_checkin['user']
        last_checkin = None
        current_path = []

    # check if this is the first checkin
    if last_checkin is not None:

        # check if the current checkin has the same venue of the last one
        if current_checkin['venue'] == last_checkin['venue']:
            num_same_venue += 1
            last_checkin = current_checkin

            # skip the current checkin
            continue
        
        # check if the current checkin was created in less than a minute from the last one
        if current_checkin['timestamp'] < last_checkin['timestamp'] + timedelta(minutes=1):
            num_invalid_time += 1
            last_checkin = current_checkin

            # skip the current checkin
            continue
        
        # check if the user is moving too fast
        if invalid_speed(last_checkin, current_checkin):
            num_invalid_speed += 1
            last_checkin = current_checkin

            # skip the current checkin
            continue

        # check if they belong to the same path
        if current_checkin['timestamp'] < last_checkin['timestamp'] + timedelta(hours=8):

            # check if this is the second checkin
            if len(current_path) == 0:
                current_path.append(last_checkin['venue'])
                save_checkin(last_checkin, new_path=True)

            # save the current checkin
            current_path.append(current_checkin['venue'])
            save_checkin(current_checkin)

        else:
            # this is the first checkin of a new path
            last_checkin = None
            current_path = []

    # for the next iteration
    last_checkin = current_checkin

print("Number of checkins with the same venue:", num_same_venue)
print("Number of checkins with invalid time:", num_invalid_time)
print("Number of checkins with invalid speed:", num_invalid_speed)

if checkin_counter is not None:
    checkins_per_path.append(checkin_counter)
checkins_per_path = np.array(checkins_per_path)
np.save('checkins_per_path.npy', checkins_per_path)
print("Number of valid checkins:", np.sum(checkins_per_path))
print("Number of paths:", len(checkins_per_path))

if initial_timestamp is not None:
    timedelta_per_path.append(last_timestamp - initial_timestamp)
timedelta_per_path = np.array(timedelta_per_path)
np.save('timedelta_per_path.npy', timedelta_per_path)

assert len(checkins_per_path) == len(timedelta_per_path)
