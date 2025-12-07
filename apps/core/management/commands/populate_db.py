"""
Django management command to populate the database with sample data.
Run with: python manage.py populate_db
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
import random

from apps.users.models import User
from apps.products.models import ProductGroup, UnitOfMeasure, Supplier, ProductMaster
from apps.quality.models import TestMethod, TestParameter, ProductSpecification
from apps.testing.models import TestRequest, TestResult


class Command(BaseCommand):
    help = 'Populates the database with sample data for demo purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            TestResult.objects.all().delete()
            TestRequest.objects.all().delete()
            ProductSpecification.objects.all().delete()
            ProductMaster.objects.all().delete()
            Supplier.objects.all().delete()
            TestParameter.objects.all().delete()
            TestMethod.objects.all().delete()
            UnitOfMeasure.objects.all().delete()
            ProductGroup.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS('Starting database population...'))

        # 1. Create Users
        self.create_users()

        # 2. Create Product Groups
        groups = self.create_product_groups()

        # 3. Create Units of Measure
        units = self.create_units()

        # 4. Create Suppliers
        suppliers = self.create_suppliers()

        # 5. Create Products
        products = self.create_products(groups, units)

        # 6. Create Test Methods
        methods = self.create_test_methods()

        # 7. Create Test Parameters
        parameters = self.create_test_parameters()

        # 8. Create Product Specifications
        self.create_specifications(products, parameters, methods)

        # 9. Create Test Requests
        test_requests = self.create_test_requests(products, suppliers)

        # 10. Create Test Results
        self.create_test_results(test_requests, parameters)

        self.stdout.write(self.style.SUCCESS('\n✅ Database populated successfully!'))

    def create_users(self):
        """Create admin and controller users"""
        self.stdout.write('Creating users...')
        
        # Admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@bichitras.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(f'  ✓ Created admin user: {admin.username}')

        # Controller users
        controllers = [
            {'username': 'controller1', 'first_name': 'John', 'last_name': 'Doe'},
            {'username': 'controller2', 'first_name': 'Jane', 'last_name': 'Smith'},
            {'username': 'controller3', 'first_name': 'Mike', 'last_name': 'Johnson'},
        ]
        
        for ctrl_data in controllers:
            controller, created = User.objects.get_or_create(
                username=ctrl_data['username'],
                defaults={
                    'email': f"{ctrl_data['username']}@bichitras.com",
                    'first_name': ctrl_data['first_name'],
                    'last_name': ctrl_data['last_name'],
                    'role': 'CONTROLLER',
                }
            )
            if created:
                controller.set_password('controller123')
                controller.save()
                self.stdout.write(f'  ✓ Created controller: {controller.username}')

    def create_product_groups(self):
        """Create product groups with hierarchy"""
        self.stdout.write('Creating product groups...')
        
        groups_data = [
            {'code': 'RM-GRAIN', 'name': 'Grains', 'parent': None},
            {'code': 'RM-PROTEIN', 'name': 'Protein Sources', 'parent': None},
            {'code': 'RM-ADDITIVE', 'name': 'Additives', 'parent': None},
            {'code': 'FG-FEED', 'name': 'Animal Feed', 'parent': None},
            {'code': 'FG-PREMIX', 'name': 'Premix', 'parent': None},
            {'code': 'IH-BLEND', 'name': 'Blended Products', 'parent': None},
            {'code': 'FF-POULTRY', 'name': 'Poultry Feed', 'parent': 'FG-FEED'},
            {'code': 'FF-CATTLE', 'name': 'Cattle Feed', 'parent': 'FG-FEED'},
        ]
        
        groups = {}
        for data in groups_data:
            parent = groups.get(data['parent']) if data['parent'] else None
            group, created = ProductGroup.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'parent_group': parent,
                    'description': f"Category for {data['name']}",
                }
            )
            groups[data['code']] = group
            if created:
                self.stdout.write(f'  ✓ Created group: {group.name}')

        return list(groups.values())

    def create_units(self):
        """Create units of measure"""
        self.stdout.write('Creating units of measure...')
        
        units_data = [
            {'name': 'Kilograms', 'symbol': 'kg'},
            {'name': 'Grams', 'symbol': 'g'},
            {'name': 'Liters', 'symbol': 'l'},
            {'name': 'Milliliters', 'symbol': 'ml'},
            {'name': 'Pieces', 'symbol': 'pcs'},
            {'name': 'Tons', 'symbol': 'kg'},  # Using kg symbol for tons
        ]
        
        units = []
        for data in units_data:
            unit, created = UnitOfMeasure.objects.get_or_create(
                name=data['name'],
                defaults={'symbol': data['symbol']}
            )
            units.append(unit)
            if created:
                self.stdout.write(f'  ✓ Created unit: {unit.name}')

        return units

    def create_suppliers(self):
        """Create suppliers"""
        self.stdout.write('Creating suppliers...')
        
        suppliers_data = [
            {'code': 'SUP001', 'name': 'AgriCorp India', 'city': 'Mumbai', 'rating': 5, 'status': 'approved'},
            {'code': 'SUP002', 'name': 'Grain Masters Ltd', 'city': 'Delhi', 'rating': 4, 'status': 'approved'},
            {'code': 'SUP003', 'name': 'Protein Solutions', 'city': 'Bangalore', 'rating': 5, 'status': 'approved'},
            {'code': 'SUP004', 'name': 'Feed Ingredients Co', 'city': 'Chennai', 'rating': 3, 'status': 'pending'},
            {'code': 'SUP005', 'name': 'Quality Grains Pvt', 'city': 'Pune', 'rating': 4, 'status': 'approved'},
            {'code': 'SUP006', 'name': 'Premium Suppliers', 'city': 'Hyderabad', 'rating': 2, 'status': 'rejected'},
        ]
        
        suppliers = []
        for data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                supplier_code=data['code'],
                defaults={
                    'name': data['name'],
                    'contact_person': f"Contact {data['name']}",
                    'email': f"contact@{data['code'].lower()}.com",
                    'phone': f"+91-{random.randint(9000000000, 9999999999)}",
                    'address': f"Address in {data['city']}",
                    'city': data['city'],
                    'country': 'India',
                    'rating': data['rating'],
                    'status': data['status'],
                }
            )
            suppliers.append(supplier)
            if created:
                self.stdout.write(f'  ✓ Created supplier: {supplier.name}')

        return suppliers

    def create_products(self, groups, units):
        """Create products with varied types"""
        self.stdout.write('Creating products...')
        
        products_data = [
            # Raw Materials
            {'code': 'RM001', 'name': 'Corn/Maize', 'type': 'RM', 'group': 'RM-GRAIN', 'unit': 'kg', 'buy_price': 25.50, 'mrp': 28.00},
            {'code': 'RM002', 'name': 'Soybean Meal', 'type': 'RM', 'group': 'RM-PROTEIN', 'unit': 'kg', 'buy_price': 45.00, 'mrp': 50.00},
            {'code': 'RM003', 'name': 'Wheat', 'type': 'RM', 'group': 'RM-GRAIN', 'unit': 'kg', 'buy_price': 22.00, 'mrp': 25.00},
            {'code': 'RM004', 'name': 'Fish Meal', 'type': 'RM', 'group': 'RM-PROTEIN', 'unit': 'kg', 'buy_price': 120.00, 'mrp': 135.00},
            {'code': 'RM005', 'name': 'Calcium Carbonate', 'type': 'RM', 'group': 'RM-ADDITIVE', 'unit': 'kg', 'buy_price': 15.00, 'mrp': 18.00},
            {'code': 'RM006', 'name': 'Rice Bran', 'type': 'RM', 'group': 'RM-GRAIN', 'unit': 'kg', 'buy_price': 18.00, 'mrp': 20.00},
            
            # Finished Goods
            {'code': 'FG001', 'name': 'Poultry Starter Feed', 'type': 'FG', 'group': 'FG-FEED', 'unit': 'kg', 'buy_price': 35.00, 'mrp': 42.00},
            {'code': 'FG002', 'name': 'Layer Feed Premium', 'type': 'FG', 'group': 'FG-FEED', 'unit': 'kg', 'buy_price': 38.00, 'mrp': 45.00},
            {'code': 'FG003', 'name': 'Cattle Feed Mix', 'type': 'FG', 'group': 'FG-FEED', 'unit': 'kg', 'buy_price': 32.00, 'mrp': 38.00},
            
            # In-House
            {'code': 'IH001', 'name': 'Custom Blend A', 'type': 'IH', 'group': 'IH-BLEND', 'unit': 'kg', 'buy_price': 40.00, 'mrp': 48.00},
            {'code': 'IH002', 'name': 'Custom Blend B', 'type': 'IH', 'group': 'IH-BLEND', 'unit': 'kg', 'buy_price': 42.00, 'mrp': 50.00},
            
            # Finished Feed
            {'code': 'FF001', 'name': 'Broiler Feed', 'type': 'FF', 'group': 'FF-POULTRY', 'unit': 'kg', 'buy_price': 36.00, 'mrp': 43.00},
            {'code': 'FF002', 'name': 'Dairy Cattle Feed', 'type': 'FF', 'group': 'FF-CATTLE', 'unit': 'kg', 'buy_price': 34.00, 'mrp': 40.00},
        ]
        
        products = []
        for data in products_data:
            group = next((g for g in groups if g.code == data['group']), groups[0])
            unit = next((u for u in units if u.symbol == data['unit']), units[0])
            
            product, created = ProductMaster.objects.get_or_create(
                product_code=data['code'],
                defaults={
                    'name': data['name'],
                    'generic_name': data['name'],
                    'short_name': data['code'],
                    'description': f"Description for {data['name']}",
                    'category': group,
                    'unit': unit,
                    'product_type_category': data['type'],
                    'buy_price': Decimal(str(data['buy_price'])),
                    'mrp': Decimal(str(data['mrp'])),
                    'cost_price': Decimal(str(data['buy_price'] * 0.95)),
                    'quantity': random.randint(50, 500),
                    'min_quantity': 50,
                    'max_quantity': 500,
                    'status': random.choice(['active', 'active', 'active', 'pending']),  # Mostly active
                    'is_batch_tracked': True,
                }
            )
            products.append(product)
            if created:
                self.stdout.write(f'  ✓ Created product: {product.name}')

        return products

    def create_test_methods(self):
        """Create test methods"""
        self.stdout.write('Creating test methods...')
        
        methods_data = [
            {'code': 'ISO6579', 'name': 'Microbiology - Salmonella Detection', 'org': 'ISO'},
            {'code': 'AOAC920.87', 'name': 'Moisture in Animal Feed', 'org': 'AOAC'},
            {'code': 'ASTMD123', 'name': 'Protein Content Analysis', 'org': 'ASTM'},
            {'code': 'ISO6496', 'name': 'Moisture Content Determination', 'org': 'ISO'},
            {'code': 'AOAC942.05', 'name': 'Ash Content in Feed', 'org': 'AOAC'},
            {'code': 'ISO16050', 'name': 'Aflatoxin B1 Detection', 'org': 'ISO'},
        ]
        
        methods = []
        for data in methods_data:
            method, created = TestMethod.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'description': f"Standard method {data['code']} for {data['name']}",
                    'standard_organization': data['org'],
                }
            )
            methods.append(method)
            if created:
                self.stdout.write(f'  ✓ Created method: {method.code}')

        return methods

    def create_test_parameters(self):
        """Create test parameters"""
        self.stdout.write('Creating test parameters...')
        
        parameters_data = [
            {'name': 'Moisture', 'type': 'Numeric'},
            {'name': 'Protein', 'type': 'Numeric'},
            {'name': 'Ash Content', 'type': 'Numeric'},
            {'name': 'Fat Content', 'type': 'Numeric'},
            {'name': 'Fiber Content', 'type': 'Numeric'},
            {'name': 'Aflatoxin B1', 'type': 'Numeric'},
            {'name': 'Salmonella', 'type': 'Boolean'},
            {'name': 'Color', 'type': 'Text'},
            {'name': 'Odor', 'type': 'Text'},
            {'name': 'Texture', 'type': 'Text'},
        ]
        
        parameters = []
        for data in parameters_data:
            param, created = TestParameter.objects.get_or_create(
                name=data['name'],
                defaults={'data_type': data['type']}
            )
            parameters.append(param)
            if created:
                self.stdout.write(f'  ✓ Created parameter: {param.name}')

        return parameters

    def create_specifications(self, products, parameters, methods):
        """Create product specifications"""
        self.stdout.write('Creating product specifications...')
        
        # Define specifications for different product types
        specs_map = {
            'RM': {  # Raw Materials
                'Moisture': {'min': 10, 'max': 14, 'unit': '%', 'method': 'ISO6496'},
                'Protein': {'min': 8, 'max': 12, 'unit': '%', 'method': 'ASTMD123'},
                'Ash Content': {'min': 1, 'max': 3, 'unit': '%', 'method': 'AOAC942.05'},
                'Aflatoxin B1': {'min': 0, 'max': 20, 'unit': 'ppb', 'method': 'ISO16050'},
                'Salmonella': {'standard': 'Negative', 'method': 'ISO6579'},
            },
            'FG': {  # Finished Goods
                'Moisture': {'min': 10, 'max': 12, 'unit': '%', 'method': 'AOAC920.87'},
                'Protein': {'min': 16, 'max': 20, 'unit': '%', 'method': 'ASTMD123'},
                'Fat Content': {'min': 3, 'max': 5, 'unit': '%', 'method': 'ASTMD123'},
                'Ash Content': {'min': 5, 'max': 8, 'unit': '%', 'method': 'AOAC942.05'},
            },
            'FF': {  # Finished Feed
                'Moisture': {'min': 10, 'max': 12, 'unit': '%', 'method': 'AOAC920.87'},
                'Protein': {'min': 18, 'max': 22, 'unit': '%', 'method': 'ASTMD123'},
                'Fat Content': {'min': 3, 'max': 6, 'unit': '%', 'method': 'ASTMD123'},
            },
        }
        
        count = 0
        for product in products:
            product_type = product.product_type_category
            specs = specs_map.get(product_type, specs_map['RM'])
            
            for param_name, spec_data in specs.items():
                param = next((p for p in parameters if p.name == param_name), None)
                if not param:
                    continue
                
                method = next((m for m in methods if m.code == spec_data.get('method', '')), None)
                
                spec, created = ProductSpecification.objects.get_or_create(
                    product=product,
                    parameter=param,
                    defaults={
                        'min_value': Decimal(str(spec_data.get('min', 0))) if param.data_type == 'Numeric' else None,
                        'max_value': Decimal(str(spec_data.get('max', 100))) if param.data_type == 'Numeric' else None,
                        'target_value': str((spec_data.get('min', 0) + spec_data.get('max', 100)) / 2) if param.data_type == 'Numeric' else '',
                        'standard_text_value': spec_data.get('standard', ''),
                        'unit': spec_data.get('unit', ''),
                        'test_method': method,
                        'is_critical': param_name in ['Aflatoxin B1', 'Salmonella'],
                    }
                )
                if created:
                    count += 1

        self.stdout.write(f'  ✓ Created {count} specifications')

    def create_test_requests(self, products, suppliers):
        """Create test requests with varied statuses and dates"""
        self.stdout.write('Creating test requests...')
        
        controllers = list(User.objects.filter(role='CONTROLLER'))
        if not controllers:
            self.stdout.write(self.style.ERROR('  ✗ No controllers found!'))
            return []
        
        statuses = ['Pending', 'In-Progress', 'Submitted for Review', 'Completed', 'Approved', 'Rejected']
        status_weights = [0.1, 0.15, 0.2, 0.15, 0.3, 0.1]  # More approved, fewer rejected
        
        test_requests = []
        base_date = timezone.now().date()
        
        for i in range(50):  # Create 50 test requests
            days_ago = random.randint(0, 90)  # Last 90 days
            sample_date = base_date - timedelta(days=days_ago)
            
            status = random.choices(statuses, weights=status_weights)[0]
            
            # Set current_step based on status
            if status == 'Pending':
                current_step = 1
            elif status == 'In-Progress':
                current_step = random.randint(2, 3)
            elif status in ['Submitted for Review', 'Completed', 'Approved', 'Rejected']:
                current_step = 4
            else:
                current_step = random.randint(1, 4)
            
            batch_number = f"BATCH-{sample_date.strftime('%Y%m%d')}-{i+1:03d}"
            
            test_request = TestRequest.objects.create(
                batch_number=batch_number,
                product=random.choice(products),
                supplier=random.choice(suppliers) if random.random() > 0.2 else None,  # 80% have supplier
                controller_user=random.choice(controllers),
                status=status,
                sample_date=sample_date,
                current_step=current_step,
                remarks=random.choice([
                    '', 'Standard quality check', 'Routine testing', 
                    'Customer complaint investigation', 'New supplier verification'
                ]) if random.random() > 0.5 else '',
            )
            test_requests.append(test_request)
            
            if (i + 1) % 10 == 0:
                self.stdout.write(f'  ✓ Created {i + 1} test requests...')

        self.stdout.write(f'  ✓ Created {len(test_requests)} test requests')
        return test_requests

    def create_test_results(self, test_requests, parameters):
        """Create test results with varied pass/fail statuses"""
        self.stdout.write('Creating test results...')
        
        controllers = list(User.objects.filter(role='CONTROLLER'))
        
        total_results = 0
        for test_request in test_requests:
            # Get specifications for this product
            specs = ProductSpecification.objects.filter(
                product=test_request.product,
                is_active=True
            ).select_related('parameter')
            
            if not specs.exists():
                continue
            
            # Create results for 3-6 parameters per test
            num_results = random.randint(3, min(6, specs.count()))
            selected_specs = random.sample(list(specs), num_results)
            
            for spec in selected_specs:
                param = spec.parameter
                
                # Generate actual value based on specification
                if param.data_type == 'Numeric':
                    if spec.min_value and spec.max_value:
                        # 70% pass, 30% fail
                        if random.random() < 0.7:
                            # Pass: value within range
                            actual = float(spec.min_value) + (float(spec.max_value) - float(spec.min_value)) * random.uniform(0.2, 0.8)
                        else:
                            # Fail: value outside range
                            if random.random() < 0.5:
                                actual = float(spec.min_value) - random.uniform(1, 5)  # Below min
                            else:
                                actual = float(spec.max_value) + random.uniform(1, 5)  # Above max
                        actual_value = f"{actual:.2f}"
                    else:
                        actual_value = f"{random.uniform(10, 20):.2f}"
                
                elif param.data_type == 'Boolean':
                    actual_value = random.choice(['Negative', 'Positive', 'Pass', 'Fail'])
                
                else:  # Text
                    actual_value = random.choice(['Normal', 'Good', 'Acceptable', 'Standard'])
                
                # Create test result
                result = TestResult.objects.create(
                    test_request=test_request,
                    parameter=param,
                    actual_value=actual_value,
                    tested_by=random.choice(controllers) if controllers else None,
                )
                
                # Calculate pass/fail (this will be done automatically by save method)
                result.calculate_pass_fail()
                total_results += 1
        
        self.stdout.write(f'  ✓ Created {total_results} test results')