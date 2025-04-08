import json
from datetime import datetime
from py3dbp import Packer, Bin, Item, Painter

# Load items from data.json
def load_items_from_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    items = []
    def get_color(priority):
        # Slightly toned-down dark red for high priority
        red_intensity = max(50, 255 - int(priority * 2))
        return f'#{red_intensity:02x}0000'

    for i, item in enumerate(data):
        try:
            expiry_date = datetime.strptime(item.get('Expiry', '9999-12-31'), '%Y-%m-%d').date()
            days_before_expiry = (expiry_date - datetime.today().date()).days
        except (ValueError, TypeError):
            days_before_expiry = 10000000000000

        priority = int(item.get('Priority', 1))
        color = get_color(priority)
        
        items.append(Item(
            partno=item.get('Item ID', 'Unknown'),
            name=item.get('Name'),
            typeof='cube',
            WHD=(item['Width'], item['Height'], item['Length']),
            weight=float(item['Weight']),
            level=priority,
            expiry=days_before_expiry,
            loadbear=100,
            updown=True,
            color=color
        ))
    return items

# Initialize packing function
packer = Packer()

# Initialize bin
box = Bin('example6', (100, 100, 100), 100000, 0, 0)
packer.addBin(box)

# Add items from JSON
items = load_items_from_json('data.json')
for item in items:
    packer.addItem(item)

# Calculate packing
packer.pack(
    bigger_first=False,
    distribute_items=False,
    fix_point=False,
    check_stable=False,
    support_surface_ratio=0,
    number_of_decimals=0
)

# Put order
packer.putOrder()

# Print result
b = packer.bins[0]
volume = b.width * b.height * b.depth
print(":::::::::::", b.string())

print("FITTED ITEMS:")
volume_t = 0
volume_f = 0
unfitted_name = ''
for item in b.items:
    print("partno : ", item.partno)
    print("color : ", item.color)
    print("position : ", item.position)
    print("rotation type : ", item.rotation_type)
    print("W*H*D : ", f"{item.width}*{item.height}*{item.depth}")
    print("volume : ", float(item.width) * float(item.height) * float(item.depth))
    print("weight : ", float(item.weight))
    print("level : ", float(item.level))
    print("days before expiry : ", int(item.expiry))
    volume_t += float(item.width) * float(item.height) * float(item.depth)
    print("***************************************************")

print("***************************************************")
print("UNFITTED ITEMS:")
for item in b.unfitted_items:
    print("partno : ", item.partno)
    print("color : ", item.color)
    print("W*H*D : ", f"{item.width}*{item.height}*{item.depth}")
    print("volume : ", float(item.width) * float(item.height) * float(item.depth))
    print("weight : ", float(item.weight))
    volume_f += float(item.width) * float(item.height) * float(item.depth)
    unfitted_name += f'{item.partno},'
    print("***************************************************")

print("***************************************************")
print(f'space utilization : {round(volume_t / float(volume) * 100, 2)}%')
print(f'residual volume : {float(volume) - volume_t}')
print(f'unpack item : {unfitted_name}')
print(f'unpack item volume : {volume_f}')
print("gravity distribution : ", b.gravity)

# Draw results
painter = Painter(b)
fig = painter.plotBoxAndItems(
    title=b.partno,
    alpha=0.8,
    write_num=False,
    fontsize=10
)
fig.show()
