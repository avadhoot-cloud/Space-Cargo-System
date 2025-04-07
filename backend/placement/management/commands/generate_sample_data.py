import os
import pandas as pd
import numpy as np
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Generate sample CSV data for the Space Cargo System'

    def handle(self, *args, **kwargs):
        # Create data directory if it doesn't exist
        data_dir = settings.DATA_DIR
        data_dir.mkdir(exist_ok=True)
        
        # Generate sample containers
        self.stdout.write('Generating sample containers...')
        containers = []
        zones = ['storage', 'lab', 'medical', 'maintenance']
        
        for i in range(1, 5):
            # Create different types of containers
            if i == 1:
                # Large storage container
                containers.append({
                    'container_id': i,
                    'name': f'Storage Container {i}',
                    'width_cm': 150,
                    'height_cm': 120,
                    'depth_cm': 200,
                    'max_weight_kg': 500,
                    'zone': 'storage'
                })
            elif i == 2:
                # Medium lab container
                containers.append({
                    'container_id': i,
                    'name': f'Lab Container {i}',
                    'width_cm': 100,
                    'height_cm': 90,
                    'depth_cm': 120,
                    'max_weight_kg': 300,
                    'zone': 'lab'
                })
            elif i == 3:
                # Small medical container
                containers.append({
                    'container_id': i,
                    'name': f'Medical Container {i}',
                    'width_cm': 80,
                    'height_cm': 70,
                    'depth_cm': 90,
                    'max_weight_kg': 150,
                    'zone': 'medical'
                })
            else:
                # Maintenance container
                containers.append({
                    'container_id': i,
                    'name': f'Maintenance Container {i}',
                    'width_cm': 120,
                    'height_cm': 100,
                    'depth_cm': 150,
                    'max_weight_kg': 350,
                    'zone': 'maintenance'
                })
        
        # Create DataFrame and save to CSV
        containers_df = pd.DataFrame(containers)
        containers_df.to_csv(data_dir / 'containers.csv', index=False)
        self.stdout.write(self.style.SUCCESS(f'Generated {len(containers)} containers'))
        
        # Generate sample items
        self.stdout.write('Generating sample items...')
        items = []
        item_names = ['Box', 'Equipment', 'Supplies', 'Tool', 'Container']
        
        for i in range(1, 6):
            # Create different types of items
            name = f'{np.random.choice(item_names)} {i}'
            width = np.random.randint(20, 50)
            height = np.random.randint(15, 40)
            depth = np.random.randint(25, 60)
            weight = round(np.random.uniform(1, 15), 1)
            priority = np.random.randint(1, 5)
            preferred_zone = np.random.choice(zones)
            
            items.append({
                'item_id': i,
                'name': name,
                'width_cm': width,
                'height_cm': height,
                'depth_cm': depth,
                'weight_kg': weight,
                'priority': priority,
                'preferred_zone': preferred_zone
            })
        
        # Create DataFrame and save to CSV
        items_df = pd.DataFrame(items)
        items_df.to_csv(data_dir / 'input_items.csv', index=False)
        self.stdout.write(self.style.SUCCESS(f'Generated {len(items)} items'))
        
        # Generate empty placement result files
        pd.DataFrame(columns=[
            'item_id', 'container_id', 'x_cm', 'y_cm', 'z_cm', 
            'rotation', 'width', 'height', 'depth', 'priority', 'sensitive'
        ]).to_csv(data_dir / 'placed_items.csv', index=False)
        
        pd.DataFrame(columns=[
            'item_id', 'name', 'reason'
        ]).to_csv(data_dir / 'unplaced_items.csv', index=False)
        
        self.stdout.write(self.style.SUCCESS('Generated empty placement result files'))
        self.stdout.write(self.style.SUCCESS(f'Sample data has been generated in {data_dir}')) 