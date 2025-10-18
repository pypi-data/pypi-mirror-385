# **Holehe OSINT - Email to Registered Accounts**
👋 Hi there! For any professional inquiries or collaborations, please reach out to me at:
gsksvsksksj@gmail.com

📧 Preferably, use your professional email for correspondence. Let's keep it short and sweet, and all in English!


### 📈 Python Example

```python
import trio
import httpx

from holehe.modules.social_media.snapchat import snapchat


async def main():
    email = "test@gmail.com"
    out = []
    client = httpx.AsyncClient()

    await snapchat(email, client, out)

    print(out)
    await client.aclose()

trio.run(main)
```