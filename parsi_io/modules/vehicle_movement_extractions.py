import re

from parsi_io.modules.address_extractor.address_extractions import AddressExtraction


class VehicleMovementExtraction:
    def __init__(self):
        car_models = r"آئودی|آستون مارتین|آلفا رومئو|اوپل|اویکو|اسکودا|ایسوزو|بنتلی|بوگاتی|امویام|بیسو|بی ام و|پژو|پورشه|گریتوال|جیامسی|جیلی|پونتیاک|پورش|تویوتا|جگوار|جاگوار|جیپ|دانگفنگ|بیامو|چری|رنو|رولزرویس|سیناد|سوزوکی|آلفارومئو|سیتروئن|گکگونو|بایک|اپل|اندرور|شورلت|شورولت|فراری|فوتون|فورد|بیوک|راین|بسترن|فولکس|بیوایدی|کوپا|برلیانس|سئات|فاو|فولکس واگن|هنتنگ|فیات|هاوال|کادیلاک|زوتی|دلیکا|الدزمبیل|لامبورگینی|روور|لندمارک|لندروور|لکسوس|مازراتی|مزدا|بنز|مرسدس بنز|میتسوبیشی|نیسان|هوندا|هیوندا|هیوندای|ولوو|ام وی ام|جاماس|جک|سوبارو|آمیکو|سانگیانگ|امجی|ام جی|تریومف|کیا|لادا|دوج|کرایسلر|لندروور|لاندروفر|۲۰۶|۲۰۷|۲۰۷i|۴۰۵|۱۱۱|۱۳۲|۱۴۱|۳۰۱|۵۰۸|۲۰۰۸|تیبا|پراید|آریو|سابرینا|سایپا|ساینا|کوییک|زانتیا|ریو|مگان|بریلیانس|ماکسیما|پرشیا|سراتو|چانگان|رانا|رانا پلاس|دنا|زامیاد|دنا پلاس|آریسان|اسمارت|تارا|تندر|سمند|سورن|پارس|پیکاپ|کپچر|کیزاشی|ویتارا|تندر|پیکان|دانگ فنگ|کاپرا|وستفیلد|اینفینیتی|هافیلوب|لینکلن|لیفان|مینیماینر|پروتون|کاکی|پاژن|دیاس|هایما|هامر|دوو|آریسان"
        self.car_models_pattern = re.compile(
            f"با (خودرو|خودروی|ماشین) ({car_models})")

        self.vehicle_names = r"اتوبوس|قطار|خودرو|ماشین|موتور|هواپیما|کشتی|قایق|مینی بوس|تریلی|مترو|تاکسی|هلی کوپتر|بالگرد|دوچرخه|ون|آژانس|موتور سیکلت|موتورسیکلت|کامیون|تراموا|طیاره|جت|آژانس|سواری|وانت|فضاپیما"
        self.vehicle_names = f"{self.vehicle_names}|اسب|قاطر|شتر|الاغ|گاری|درشکه|دلیجان|{car_models}"
        self.vehicle_pattern = re.compile(f"(با|به وسیله|بوسیله|به وسیله ی|بوسیله ی) ({self.vehicle_names})")
        self.from_pattern = re.compile(r'از \w+')
        self.to_pattern = re.compile(r'(به|به سوی|بسوی|به سمت|بسمت|به طرف|بطرف) \w+')

    def __get_car_model_match(self, text: str):
        iterator = list(re.finditer(self.car_models_pattern, text))
        if not iterator:
            return None

        text = iterator[0].group()

        for c in ['خودرو', 'خودروی', 'ماشین']:
            if text[3:].startswith(f"{c} "):
                return text[4 + len(c):], iterator[0].start() + 4 + len(c), iterator[0].end()
        assert False

    def __get_vehicle_match(self, text: str) -> tuple:
        car_model_match = self.__get_car_model_match(text)
        if car_model_match:
            return car_model_match

        iterator = list(re.finditer(self.vehicle_pattern, text))
        assert len(iterator) == 1
        text = iterator[0].group()

        for s in ["با", "به وسیله", "بوسیله", "به وسیله ی", "بوسیله ی"]:
            if text.startswith(f"{s} "):
                return text[len(s) + 1:], iterator[0].start() + len(s) + 1, iterator[0].end()
        

    def match_vehicles(self, text: str) -> tuple:
        vehicle, vehicle_start, vehicle_end = self.__get_vehicle_match(text)
        return vehicle, [vehicle_start, vehicle_end]

    def __match_address(self, text: str, pattern: re.Pattern) -> tuple:
        address_ = ""
        address_start = -1
        address_end = -1

        iterator = list(re.finditer(pattern, text))

        for itr in iterator:
            address = AddressExtraction().run(itr.group())
            if address['address']:
                assert len(address['address']) == 1
                address_ = address['address'][0]
                address_start = address['address_span'][0] + itr.start()
                address_end = address['address_span'][1] + itr.start()
        return address_, [address_start, address_end]

    def match_from(self, text: str) -> tuple:
        return self.__match_address(text, self.from_pattern)

    def match_to(self, text: str) -> tuple:
        return self.__match_address(text, self.to_pattern)

    def run(self, text: str) -> list:
        # replace half-space with space
        text = text.replace("\u200C", " ")

        vehicle, vehicle_span = self.match_vehicles(text)
        from_, from_span = self.match_from(text)
        to, to_span = self.match_to(text)
        return [
            {
                "from": from_,
                "from_span": from_span,
                "to": to,
                "to_span": to_span,
                "vehicle": vehicle,
                "vehicle_span": vehicle_span,
            },
        ]


if __name__ == '__main__':
    model = VehicleMovementExtraction()
    input_text = input()
    print(model.run(input_text))
