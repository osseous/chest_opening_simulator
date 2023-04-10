import csv
import random
import yaml
import asyncio
from tqdm import tqdm


def get_item(box):
    return random.choices(box['items'], [item['probability'] for item in box['items']])[0]


async def open_box(config, box):
    items = []
    for i in range(config['OpeningsPerPlayer']):
        item = get_item(config['Boxes'][box])
        items.append(item['name'])
        await asyncio.sleep(0)  # to simulate some work
    return items


async def open_boxes(config, boxes, pbar=None):
    tasks = []
    for box in boxes:
        tasks.append(asyncio.create_task(open_box(config, box)))
    boxes_results = await asyncio.gather(*tasks)
    results = {}
    for i, box in enumerate(boxes):
        results[box] = boxes_results[i]
        if pbar:
            pbar.update(1)
    return results


async def generate_csv(config, boxes):
    headers = ['Player']
    items_counts = {item['name']: 0 for item in config['Boxes'][boxes[0]]['items']}
    for box in boxes:
        for item in config['Boxes'][box]['items']:
            item_name = item['name']
            if item_name not in items_counts:
                items_counts[item_name] = 0
                headers.append(item_name)
    results = [headers]

    for i in range(config['NumOfPlayer']):
        row = [f"Player{i + 1:0{5}}"]
        items = items_counts.copy()
        boxes_results = await open_boxes(config, boxes)
        for box in boxes:
            items_list = boxes_results[box]
            for item_name in items_list:
                items[item_name] += 1
        for count in items.values():
            row.append(count)
        results.append(row)

    with open('out.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(results)


if __name__ == '__main__':
    with open('lootbox_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    boxes = list(config['Boxes'].keys())
    asyncio.run(generate_csv(config, boxes))
