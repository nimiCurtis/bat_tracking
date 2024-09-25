import h5py
with h5py.File('/home/roblab20/dev/sleap_bat_tracking/labels.v001.000_Oskar with food (1).analysis.h5', 'r') as f:
    occupancy_matrix = f['track_occupancy'][:]
    tracks_matrix = f['tracks'][:]

print(occupancy_matrix.shape)
print(tracks_matrix.shape)