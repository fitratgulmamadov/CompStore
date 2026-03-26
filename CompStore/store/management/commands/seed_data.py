from django.core.management.base import BaseCommand
from store.models import Category, Product, PrebuiltPC, PrebuiltComponent, PrebuiltLevel


class Command(BaseCommand):
    help = 'Заполнить базу тестовыми данными'

    def handle(self, *args, **options):
        self.stdout.write('Создаём категории...')

        categories_data = [
            ('Процессоры', 'cpu', 'bi-cpu', 1),
            ('Видеокарты', 'gpu', 'bi-gpu-card', 2),
            ('Оперативная память', 'ram', 'bi-memory', 3),
            ('Материнские платы', 'motherboard', 'bi-motherboard', 4),
            ('Накопители', 'storage', 'bi-device-hdd', 5),
            ('Блоки питания', 'psu', 'bi-lightning-charge', 6),
            ('Корпуса', 'case', 'bi-box', 7),
            ('Охлаждение', 'cooling', 'bi bi-fan', 8),
        ]

        cats = {}
        for name, ctype, icon, order in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=ctype,
                defaults={'name': name, 'type': ctype, 'icon': icon, 'order': order}
            )
            cats[ctype] = cat
            self.stdout.write(f'  ✓ {name}')

        self.stdout.write('Создаём товары...')

        products_data = [
            # CPUs
            {
                'cat': 'cpu', 'brand': 'AMD', 'name': 'Ryzen 5 5600X',
                'price': 1950, 'old_price': 2184,
                'socket': 'AM4', 'is_featured': True,
                'specs': {'Ядра': '6', 'Потоки': '12', 'Частота': '3.7 / 4.6 GHz', 'TDP': '65W', 'Сокет': 'AM4'},
                'description': 'Отличный процессор для игровых ПК. 6 ядер, 12 потоков, техпроцесс 7нм.'
            },
            {
                'cat': 'cpu', 'brand': 'AMD', 'name': 'Ryzen 7 7800X3D',
                'price': 4056, 'socket': 'AM5', 'is_featured': True,
                'specs': {'Ядра': '8', 'Потоки': '16', 'Частота': '4.2 / 5.0 GHz', 'TDP': '120W', 'Сокет': 'AM5'},
                'description': 'Лучший игровой процессор с технологией 3D V-Cache.'
            },
            {
                'cat': 'cpu', 'brand': 'Intel', 'name': 'Core i5-13600K',
                'price': 2418, 'socket': 'LGA1700',
                'specs': {'Ядра': '14 (6P+8E)', 'Потоки': '20', 'Частота': '3.5 / 5.1 GHz', 'TDP': '125W', 'Сокет': 'LGA1700'},
                'description': 'Мощный процессор Intel 13-го поколения для игр и работы.'
            },
            {
                'cat': 'cpu', 'brand': 'Intel', 'name': 'Core i9-13900K',
                'price': 5850, 'socket': 'LGA1700', 'is_featured': True,
                'specs': {'Ядра': '24 (8P+16E)', 'Потоки': '32', 'Частота': '3.0 / 5.8 GHz', 'TDP': '253W', 'Сокет': 'LGA1700'},
                'description': 'Топовый процессор для профессиональных задач и игр.'
            },
            {
                'cat': 'cpu', 'brand': 'AMD', 'name': 'Ryzen 5 5500',
                'price': 1092, 'socket': 'AM4',
                'specs': {'Ядра': '6', 'Потоки': '12', 'Частота': '3.6 / 4.2 GHz', 'TDP': '65W', 'Сокет': 'AM4'},
                'description': 'Бюджетный процессор для повседневных задач.'
            },

            # GPUs
            {
                'cat': 'gpu', 'brand': 'NVIDIA', 'name': 'GeForce RTX 4070',
                'price': 7644, 'is_featured': True,
                'specs': {'Память': '12 GB GDDR6X', 'Шина': '192-bit', 'TDP': '200W', 'Разъём': 'PCIe 4.0 x16'},
                'description': 'Отличная видеокарта для 1440p и 4K гейминга.'
            },
            {
                'cat': 'gpu', 'brand': 'AMD', 'name': 'Radeon RX 7700 XT',
                'price': 5616,
                'specs': {'Память': '12 GB GDDR6', 'Шина': '192-bit', 'TDP': '245W'},
                'description': 'Высокопроизводительная видеокарта AMD для игр.'
            },
            {
                'cat': 'gpu', 'brand': 'NVIDIA', 'name': 'GeForce RTX 3060',
                'price': 3510,
                'specs': {'Память': '12 GB GDDR6', 'Шина': '192-bit', 'TDP': '170W'},
                'description': 'Популярная видеокарта для 1080p гейминга.'
            },
            {
                'cat': 'gpu', 'brand': 'NVIDIA', 'name': 'GeForce RTX 4090',
                'price': 17160, 'is_featured': True,
                'specs': {'Память': '24 GB GDDR6X', 'Шина': '384-bit', 'TDP': '450W'},
                'description': 'Самая мощная потребительская видеокарта.'
            },
            {
                'cat': 'gpu', 'brand': 'AMD', 'name': 'Radeon RX 6600',
                'price': 2496,
                'specs': {'Память': '8 GB GDDR6', 'Шина': '128-bit', 'TDP': '132W'},
                'description': 'Отличное соотношение цена/качество.'
            },

            # RAM
            {
                'cat': 'ram', 'brand': 'Kingston', 'name': 'FURY Beast DDR4 16GB 3200MHz',
                'price': 507, 'is_featured': True, 'ram_type': 'DDR4',
                'specs': {'Объём': '16 GB', 'Тип': 'DDR4', 'Частота': '3200 MHz', 'Тайминги': 'CL16'},
                'description': 'Надёжная оперативная память для игровых ПК.'
            },
            {
                'cat': 'ram', 'brand': 'Corsair', 'name': 'Vengeance DDR5 32GB 5600MHz',
                'price': 1404, 'ram_type': 'DDR5',
                'specs': {'Объём': '32 GB', 'Тип': 'DDR5', 'Частота': '5600 MHz', 'Тайминги': 'CL36'},
                'description': 'Высокоскоростная память DDR5 нового поколения.'
            },
            {
                'cat': 'ram', 'brand': 'G.Skill', 'name': 'Trident Z5 RGB 32GB DDR5 6000MHz',
                'price': 1872, 'is_featured': True, 'ram_type': 'DDR5',
                'specs': {'Объём': '32 GB', 'Тип': 'DDR5', 'Частота': '6000 MHz', 'Тайминги': 'CL30'},
                'description': 'Топовая оперативная память с RGB подсветкой.'
            },
            {
                'cat': 'ram', 'brand': 'TeamGroup', 'name': 'T-Force Vulcan DDR4 8GB 3000MHz',
                'price': 273, 'ram_type': 'DDR4',
                'specs': {'Объём': '8 GB', 'Тип': 'DDR4', 'Частота': '3000 MHz'},
                'description': 'Бюджетная память для начального уровня.'
            },

            # Motherboards
            {
                'cat': 'motherboard', 'brand': 'ASUS', 'name': 'ROG STRIX B550-F Gaming',
                'price': 2496, 'socket': 'AM4', 'is_featured': True, 'ram_type': 'DDR4',
                'specs': {'Сокет': 'AM4', 'Чипсет': 'B550', 'Формфактор': 'ATX', 'RAM': 'DDR4'},
                'description': 'Геймерская материнская плата для процессоров AMD AM4.'
            },
            {
                'cat': 'motherboard', 'brand': 'MSI', 'name': 'MAG X670E Tomahawk WiFi',
                'price': 4290, 'socket': 'AM5', 'ram_type': 'DDR5',
                'specs': {'Сокет': 'AM5', 'Чипсет': 'X670E', 'Формфактор': 'ATX', 'RAM': 'DDR5'},
                'description': 'Топовая плата для процессоров AMD Ryzen 7000.'
            },
            {
                'cat': 'motherboard', 'brand': 'Gigabyte', 'name': 'Z790 AORUS Elite AX',
                'price': 3744, 'socket': 'LGA1700', 'ram_type': 'DDR5',
                'specs': {'Сокет': 'LGA1700', 'Чипсет': 'Z790', 'Формфактор': 'ATX', 'RAM': 'DDR5'},
                'description': 'Плата для процессоров Intel 12/13 поколения.'
            },
            {
                'cat': 'motherboard', 'brand': 'ASRock', 'name': 'B450M Pro4',
                'price': 936, 'socket': 'AM4', 'ram_type': 'DDR4',
                'specs': {'Сокет': 'AM4', 'Чипсет': 'B450', 'Формфактор': 'Micro-ATX', 'RAM': 'DDR4'},
                'description': 'Бюджетная плата для сборки на AM4.'
            },

            # Storage
            {
                'cat': 'storage', 'brand': 'Samsung', 'name': '980 Pro NVMe SSD 1TB',
                'price': 936, 'is_featured': True,
                'specs': {'Объём': '1 TB', 'Интерфейс': 'NVMe PCIe 4.0', 'Чтение': '7000 MB/s', 'Запись': '5000 MB/s'},
                'description': 'Быстрый NVMe SSD для системного диска.'
            },
            {
                'cat': 'storage', 'brand': 'WD', 'name': 'Blue SN570 NVMe 500GB',
                'price': 452,
                'specs': {'Объём': '500 GB', 'Интерфейс': 'NVMe PCIe 3.0', 'Чтение': '3500 MB/s'},
                'description': 'Бюджетный NVMe SSD.'
            },
            {
                'cat': 'storage', 'brand': 'Seagate', 'name': 'Barracuda HDD 2TB',
                'price': 351,
                'specs': {'Объём': '2 TB', 'Интерфейс': 'SATA 6Gb/s', 'RPM': '7200'},
                'description': 'Надёжный жёсткий диск для хранения данных.'
            },
            {
                'cat': 'storage', 'brand': 'Kingston', 'name': 'NV2 NVMe SSD 2TB',
                'price': 1248,
                'specs': {'Объём': '2 TB', 'Интерфейс': 'NVMe PCIe 4.0', 'Чтение': '3500 MB/s'},
                'description': 'Ёмкий SSD по доступной цене.'
            },

            # PSU
            {
                'cat': 'psu', 'brand': 'Corsair', 'name': 'RM850x 850W 80+ Gold',
                'price': 1638, 'is_featured': True,
                'specs': {'Мощность': '850 W', 'Сертификат': '80+ Gold', 'Модульность': 'Полностью модульный'},
                'description': 'Надёжный блок питания с отличной эффективностью.'
            },
            {
                'cat': 'psu', 'brand': 'Seasonic', 'name': 'Focus GX-650 650W 80+ Gold',
                'price': 1248,
                'specs': {'Мощность': '650 W', 'Сертификат': '80+ Gold', 'Модульность': 'Полностью модульный'},
                'description': 'Качественный блок питания для среднего ПК.'
            },
            {
                'cat': 'psu', 'brand': 'be quiet!', 'name': 'Straight Power 11 750W 80+ Platinum',
                'price': 2184,
                'specs': {'Мощность': '750 W', 'Сертификат': '80+ Platinum', 'Шум': 'Очень тихий'},
                'description': 'Тихий и эффективный блок питания.'
            },
            {
                'cat': 'psu', 'brand': 'EVGA', 'name': 'SuperNOVA 550 G6 550W',
                'price': 858,
                'specs': {'Мощность': '550 W', 'Сертификат': '80+ Gold'},
                'description': 'Бюджетный блок питания для небольших сборок.'
            },

            # Cases
            {
                'cat': 'case', 'brand': 'Fractal Design', 'name': 'Meshify 2 ATX',
                'price': 1794, 'is_featured': True,
                'specs': {'Формфактор': 'ATX', 'Материал': 'Сталь + закалённое стекло', 'Вентиляторы': '3x120mm в комплекте'},
                'description': 'Стильный корпус с отличной вентиляцией.'
            },
            {
                'cat': 'case', 'brand': 'NZXT', 'name': 'H510 Flow Mid-Tower',
                'price': 1404,
                'specs': {'Формфактор': 'Mid-Tower ATX', 'Материал': 'Сталь + стекло'},
                'description': 'Минималистичный корпус с хорошим воздушным потоком.'
            },
            {
                'cat': 'case', 'brand': 'Lian Li', 'name': 'O11 Dynamic EVO',
                'price': 2730,
                'specs': {'Формфактор': 'Mid-Tower ATX/E-ATX', 'Материал': 'Алюминий + стекло'},
                'description': 'Премиальный корпус для впечатляющих сборок.'
            },
            {
                'cat': 'case', 'brand': 'Deepcool', 'name': 'Matrexx 55 Mesh',
                'price': 507,
                'specs': {'Формфактор': 'Mid-Tower ATX', 'Материал': 'Сталь'},
                'description': 'Доступный корпус для бюджетных сборок.'
            },

            # Cooling
            {
                'cat': 'cooling', 'brand': 'Noctua', 'name': 'NH-D15 Chromax Black',
                'price': 1170, 'is_featured': True,
                'specs': {'Тип': 'Воздушное', 'Совместимость': 'AM4, AM5, LGA1700', 'TDP': '250W+'},
                'description': 'Лучший воздушный кулер на рынке.'
            },
            {
                'cat': 'cooling', 'brand': 'ARCTIC', 'name': 'Liquid Freezer II 240mm AIO',
                'price': 936,
                'specs': {'Тип': 'СЖО', 'Радиатор': '240mm', 'Совместимость': 'AM4, AM5, LGA1700'},
                'description': 'Эффективная система жидкостного охлаждения.'
            },
            {
                'cat': 'cooling', 'brand': 'DeepCool', 'name': 'AK620',
                'price': 585,
                'specs': {'Тип': 'Воздушное', 'TDP': '260W', 'Совместимость': 'AM4, AM5, LGA1700'},
                'description': 'Отличный двухбашенный кулер по доступной цене.'
            },
        ]

        product_objs = {}
        for data in products_data:
            cat = cats[data['cat']]
            name = data['name']
            prod, created = Product.objects.update_or_create(
                name=name,
                defaults={
                    'category': cat,
                    'brand': data['brand'],
                    'price': data['price'],
                    'old_price': data.get('old_price'),
                    'socket': data.get('socket', ''),
                    'ram_type': data.get('ram_type', ''),
                    'specs': data.get('specs', {}),
                    'description': data.get('description', ''),
                    'is_featured': data.get('is_featured', False),
                    'stock': 20,
                }
            )
            product_objs[name] = prod
            action = 'создан' if created else 'уже существует'
            self.stdout.write(f'  ✓ {name} — {action}')

        self.stdout.write('Создаём уровни сборок...')

        levels_data = [
            ('Офисный',  'bg-success', 0),
            ('Игровой',  'bg-info',    1),
            ('Топовый',  'bg-danger',  2),
        ]
        for name, color, order in levels_data:
            PrebuiltLevel.objects.get_or_create(name=name, defaults={'color': color, 'order': order})
            self.stdout.write(f'  ✓ {name}')

        self.stdout.write('Создаём готовые сборки...')

        levels = {lvl.name: lvl for lvl in PrebuiltLevel.objects.all()}

        prebuilts = [
            {
                'name': 'Бюджетный Старт',
                'slug': 'budget-start',
                'level': 'Офисный',
                'price': 4290,
                'is_featured': True,
                'description': 'Идеальная сборка для офисной работы, учёбы и лёгких игр. Стабильная производительность за разумные деньги.',
                'components': [
                    ('Ryzen 5 5500', 1),
                    ('ASRock B450M Pro4', 1),
                    ('Kingston FURY Beast DDR4 16GB 3200MHz', 1),
                    ('WD Blue SN570 NVMe 500GB', 1),
                    ('Deepcool Matrexx 55 Mesh', 1),
                    ('EVGA SuperNOVA 550 G6 550W', 1),
                ]
            },
            {
                'name': 'Игровой Мидл',
                'slug': 'gaming-mid',
                'level': 'Игровой',
                'price': 14040,
                'is_featured': True,
                'description': 'Сбалансированная игровая сборка для комфортной игры в 1080p/1440p. Отличный выбор для большинства геймеров.',
                'components': [
                    ('Ryzen 5 5600X', 1),
                    ('ASUS ROG STRIX B550-F Gaming', 1),
                    ('Kingston FURY Beast DDR4 16GB 3200MHz', 1),
                    ('Radeon RX 7700 XT', 1),
                    ('Samsung 980 Pro NVMe SSD 1TB', 1),
                    ('NZXT H510 Flow Mid-Tower', 1),
                    ('Corsair RM850x 850W 80+ Gold', 1),
                    ('DeepCool AK620', 1),
                ]
            },
            {
                'name': 'Топовая Сборка Pro',
                'slug': 'top-pro',
                'level': 'Топовый',
                'price': 35100,
                'is_featured': True,
                'description': 'Максимальная производительность для 4K гейминга, стриминга и профессиональной работы. Никаких компромиссов.',
                'components': [
                    ('Ryzen 7 7800X3D', 1),
                    ('MSI MAG X670E Tomahawk WiFi', 1),
                    ('Corsair Vengeance DDR5 32GB 5600MHz', 1),
                    ('GeForce RTX 4090', 1),
                    ('Samsung 980 Pro NVMe SSD 1TB', 1),
                    ('Seagate Barracuda HDD 2TB', 1),
                    ('Lian Li O11 Dynamic EVO', 1),
                    ('Corsair RM850x 850W 80+ Gold', 1),
                    ('ARCTIC Liquid Freezer II 240mm AIO', 1),
                ]
            },
        ]

        for pb_data in prebuilts:
            level_obj = levels.get(pb_data['level'])
            pb, created = PrebuiltPC.objects.get_or_create(
                slug=pb_data['slug'],
                defaults={
                    'name': pb_data['name'],
                    'level': level_obj,
                    'price': pb_data['price'],
                    'is_featured': pb_data['is_featured'],
                    'description': pb_data['description'],
                }
            )
            if created:
                for prod_name, qty in pb_data['components']:
                    try:
                        product = Product.objects.get(name__icontains=prod_name)
                        PrebuiltComponent.objects.get_or_create(
                            prebuilt=pb, product=product, defaults={'quantity': qty}
                        )
                    except Product.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'  ! Не найден продукт: {prod_name}'))
                    except Product.MultipleObjectsReturned:
                        self.stdout.write(self.style.WARNING(f'  ! Несколько продуктов: {prod_name}'))
                self.stdout.write(f'  ✓ Сборка "{pb_data["name"]}" создана')
            else:
                self.stdout.write(f'  - Сборка "{pb_data["name"]}" уже существует')

        self.stdout.write(self.style.SUCCESS('\n✅ База данных успешно заполнена!'))
        self.stdout.write(self.style.SUCCESS('Запустите сервер: python manage.py runserver'))
