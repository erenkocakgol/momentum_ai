# Momentum AI | developed by Eren Koçakgöl ⭐️

**Momentum AI**, interneti günlük olarak tarayarak haberleri çekip OpenAI API'si ile otomatik olarak yeniden yazarak veritabanına kaydeden bir yapay zeka uygulamasıdır. **Postafon** ile entegre çalışmak üzere tasarlanmış olup, güçlü ve esnek bir altyapı sunar.

## Not: Bu yazılım, **Postafon** gibi uygulamalarla birlikte kullanıldığında tam potansiyelini gösterir. Ancak, bağımsız olarak da kullanılabilir. Postafon ile entegrasyon için bu yazılımı kurmanız gerekmektedir.
### Postafon: [https://github.com/erenkocakgol/postafon.com](https://github.com/erenkocakgol/postafon.com)

## Bu Yazılımın,

- **Özellik 1:** Günlük internet taraması ve haber çekme,
- **Özellik 2:** OpenAI API'si ile otomatik haber yeniden yazımı,
- **Özellik 3:** Django ile veritabanına kaydetme,
- ve titiz çalışma ile geliştirilmiştir. Lütfen atıfta bulununuz. Bu gereklidir. <3

## Kurulum 💽

Momentum AI'a başlamak için bu depoyu klonlayın, **momentum_ai klasörü altında config.json dosyasını kendinize göre düzenleyin** ve gerekli bağımlılıkları yükleyin:

```bash
git clone https://github.com/erenkocakgol/momentum_ai.git

cd momentum_ai

python3 -m venv .venv

source .venv/bin/activate (Windows için farklı olduğuna dikkat edin. Bu komut macOS ve Linux Debian içindir.)

python -m pip install -r requirements.txt

cd momentum_ai

python main.py