import requests

from datetime import datetime

day_names = {
    'Monday': 'Pazartesi',
    'Tuesday': 'Salı',
    'Wednesday': 'Çarşamba',
    'Thursday': 'Perşembe',
    'Friday': 'Cuma',
    'Saturday': 'Cumartesi',
    'Sunday': 'Pazar'
}

questions = [
    {
        "id": 1,
        "text": "Bilgisayar görüşü nedir ve hangi uygulamalarda kullanılır?",
        "options": ["Görüntü işleme ve analizi için kullanılan bir alan.", "Bilgisayarların insan gözü gibi görmesini sağlayan bir teknoloji.", "Yapay zeka modellemelerinde kullanılmaz.", "Sadece sesle ilgili çalışmaları içerir."],
        "correct_answer": 1
    },
    {
        "id": 2,
        "text": "NLP nedir ve hangi uygulamalarda kullanılır?",
        "options": ["Doğal dilin bilgisayarlar tarafından anlaşılması ve işlenmesi.", "Yalnızca yazılı metinler üzerinde çalışır.", "Yapay zeka ile hiçbir ilgisi yoktur.", "Sadece sayılarla ilgilenir."],
        "correct_answer": 1
    },
    {
        "id": 3,
        "text": "Python ile hangi tür AI (Yapay Zeka) modelleri uygulanabilir?",
        "options": ["Sadece tablo verileri üzerinde çalışır.", "Görüntülerle ilgilenmez.", "NLP dışındaki AI uygulamalarında kullanılamaz.", "Görüntü işleme, NLP ve daha fazlasında AI uygulamaları yapabilir."],
        "correct_answer": 4
    },
    {
        "id": 4,
        "text": "AI geliştirme süreci nedir?",
        "options": ["Rastgele kod yazma.", "Belirli bir hedefe yönelik planlama, veri toplama, model oluşturma ve değerlendirme.", "Yalnızca büyük şirketler tarafından gerçekleştirilir.", "Sadece teorik çalışmalar içerir."],
        "correct_answer": 2
    },
    {
        "id": 5,
        "text": "Bir AI modelinin değerlendirilmesi neden önemlidir?",
        "options": ["Değerlendirme yapmanın bir gereği yoktur.", "Modelin performansını, güvenilirliğini ve uygunluğunu anlamak için.", "Sadece modelin eğitim sürecini görmek için.", "Modelin boyutunu belirlemek için."],
        "correct_answer": 2
    }
]

def get_day_name(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    day_names = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
    return day_names[date_obj.weekday()]


def get_weather(city):
    api_key = "3313c6fe6136403db75214322231310"
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=3&lang=tr"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        processed_weather_data = []
        for forecast in data['forecast']['forecastday']:
            processed_weather_data.append({
                'turkish_day': get_day_name(forecast['date']),
                'date': forecast['date'],
                'condition': forecast['day']['condition']['text'],
                'max_temp': forecast['day']['maxtemp_c'],
                'min_temp': forecast['day']['mintemp_c']
            })
        return processed_weather_data,data
    else:
        return None


def dc_search(dict_list, key, value):
    for item in dict_list:
        if item.get(key) == value:
            return item
    return None
