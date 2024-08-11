# Ahlullhaqq API | Discord Bot

This project consists of two main components:

1. **API**: Collects and organizes news related to global conflicts and wars, then provides this data through various endpoints.
2. **Discord Bot**: Fetches the formatted data from the API and posts it on Discord channels.

## How It Works

### The API

The API requests data from news websites, scrapes the needed information, and formats it into the following object:

- `img_url: Optional[str] = None`
- `title: Optional[str] = None`
- `url: Optional[str] = None`
- `date: Optional[str] = None`
- `author: Optional[str] = None`
- `brief: Optional[str] = None`
- `article_text: Optional[dict] = None`
- `source: Optional[str] = None`

The API exposes these endpoints:

- `/api/latest_news`
- `/api/shahada_agency`
- `/api/amaq_agency`
- `/api/dawla_agency`
- `/api/sources`

You can build upon this API to create your own news website or another bot. The API operates independently from the bot.

### The Bot

The bot uses the API endpoints to retrieve and format the news data, then posts it in Discord channels.

## Setup

1. Install [Docker](https://docs.docker.com/get-docker/).
2. Navigate to the base directory.
3. Edit the `docker-compose.yml` file to fit your configuration.
4. Run `docker-compose up -d` to start the services.

## Usage in Discord

1. Run the command `/check_for_new_sources`. This step is necessary for the bot to configure itself to request data from the API.
2. Run the command `add_all_sources cat:CATEGORY` to create channels where the bot will send news updates.

That's it! The bot will continue to send news updates automatically.

---

# Ahlullhaqq API | بوت ديسكورد

يتكون هذا المشروع من مكونين رئيسيين:

1. **API**: يجمع وينظم الأخبار المتعلقة بالصراعات والحروب العالمية، ثم يوفر هذه البيانات من خلال نقاط النهاية المختلفة.
2. **بوت ديسكورد**: يجلب البيانات المهيأة من الـ API وينشرها على قنوات ديسكورد.

## كيفية العمل

### الـ API

يقوم الـ API بطلب البيانات من مواقع الأخبار، ويقوم باستخلاص المعلومات اللازمة، ثم يقوم بتنسيقها في الكائن التالي:

- `img_url: Optional[str] = None`
- `title: Optional[str] = None`
- `url: Optional[str] = None`
- `date: Optional[str] = None`
- `author: Optional[str] = None`
- `brief: Optional[str] = None`
- `article_text: Optional[dict] = None`
- `source: Optional[str] = None`

يتيح الـ API النقاط النهائية التالية:

- `/api/latest_news`
- `/api/shahada_agency`
- `/api/amaq_agency`
- `/api/dawla_agency`
- `/api/sources`

### البوت

يستخدم البوت نقاط النهاية الخاصة بالـ API لاسترجاع وتنسيق بيانات الأخبار، ثم ينشرها في قنوات ديسكورد.

## الإعداد

1. قم بتثبيت [Docker](https://docs.docker.com/get-docker/).
2. انتقل إلى الفولدر الرئيسي.
3. عدل ملف `docker-compose.yml` ليتناسب مع التكوين الخاص بك.
4. قم بتشغيل `docker-compose up -d` لبدء الخدمات.

## الاستخدام في ديسكورد

1. قم بتشغيل الأمر `/check_for_new_sources`. هذه الخطوة ضرورية لكي يقوم البوت بتكوين نفسه لطلب البيانات من الـ API.
2. قم بتشغيل الأمر `add_all_sources cat:CATEGORY` لإنشاء قنوات حيث سيقوم البوت بإرسال التحديثات الإخبارية.

هذا كل شيء! سيواصل البوت إرسال التحديثات الإخبارية تلقائيًا.
