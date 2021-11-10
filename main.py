import csv
from numpy import inner
import pandas as pd
import time
start_time = time.time()

print("Loading Owners...")

#First load all the owners of property in the Auckland region, and get their Title Number and Property Type (Freehold, etc)

owners = pd.read_csv("nz-property-titles-including-owners.csv") #Load owners data
owners = owners [(owners ["land_district"] == "North Auckland")] #Filter out so just AKL
owners = owners[['title_no','owners', 'type']] #Just keep the important info

print("Done with Owners, loading parcel - titles ", time.time() - start_time)

# Then LINZ needs us to link the Title Number to the Parcel ID which lets us find the right address

parcel = pd.read_csv("nz-title-parcel-association-list.csv")[['title_no', 'par_id']] #Link to ParcelID
owner_parcel = owners.merge(parcel, on='title_no') #Link to ParcelID
print("Done with parcels, loading address - parcel")

# Then we need to link the parcel ID to the Address ID, and also drop the duplicate values that come up because of data inconsistency.

address_id = pd.read_csv("aims-address.csv")[['parcel_id','address_id']] #Just keep the important info
address_id = address_id.drop_duplicates('parcel_id', keep='first')

inner_merged = owner_parcel.merge(address_id, left_on='par_id', right_on='parcel_id')
inner_merged = inner_merged.drop_duplicates('title_no', keep='first')

print("Done with association, loading street addresses")

# We now link the Address ID to an actual address with co-ordinates

address = pd.read_csv("nz-street-address.csv") #load street address
address = address[['address_id','full_address_ascii', 'gd2000_xcoord', 'gd2000_ycoord']] #only keep the full address name
final_address = pd.merge(inner_merged, address, on='address_id')

# Finally, we then form the CSV file with the info we want, and send it to file.

#final_address = final_address[['title_no','owners', 'type', 'address_id', 'parcel_id', 'full_address_ascii', 'gd2000_xcoord', 'gd2000_ycoord']] #Just keep owner name, address, and co-ordinates

#Using abbrivated adddresses to make it easier on memory
final_address = final_address[['owners', 'type', 'full_address_ascii', 'gd2000_xcoord', 'gd2000_ycoord']] #Just keep owner name, address, and co-ordinates


print('WRITING TO CSV')
final_address.to_csv('output.csv', index=False)

print('DONE IN', time.time() - start_time)
