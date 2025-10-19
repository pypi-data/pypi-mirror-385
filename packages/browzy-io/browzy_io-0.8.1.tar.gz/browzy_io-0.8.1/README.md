<picture>
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/digital-trendz/browzy/assets/browzy-logo-light.png">
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/digital-trendz/browzy/assets/browzy-logo-dark.png">
  <img alt="Browzy Logo - Smart Browser Automation for Modern Business" src="https://github.com/digital-trendz/browzy/assets/browzy-logo-light.png" width="full">
</picture>

<div align="center">
    <picture>
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/digital-trendz/browzy/assets/browzy-banner-light.png">
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/digital-trendz/browzy/assets/browzy-banner-dark.png">
    <img alt="Smart Browser Automation for Modern Business" src="https://github.com/digital-trendz/browzy/assets/browzy-banner-light.png" width="400">
    </picture>
</div>

</br>

<div align="center">

<!-- Keep these links. Translations will automatically update with the README. -->
[Deutsch](https://www.readme-i18n.com/browzy/browzy?lang=de) |
[Español](https://www.readme-i18n.com/browzy/browzy?lang=es) |
[français](https://www.readme-i18n.com/browzy/browzy?lang=fr) |
[日本語](https://www.readme-i18n.com/browzy/browzy?lang=ja) |
[한국어](https://www.readme-i18n.com/browzy/browzy?lang=ko) |
[Português](https://www.readme-i18n.com/browzy/browzy?lang=pt) |
[Русский](https://www.readme-i18n.com/browzy/browzy?lang=ru) |
[中文](https://www.readme-i18n.com/browzy/browzy?lang=zh)

</div>

---

<div align="center">
<a href="#demos"><img src="https://media.browzy.io/badges/demos" alt="Demos"></a>
<img width="16" height="1" alt="">
<a href="https://docs.browzy.io"><img src="https://media.browzy.io/badges/docs" alt="Docs"></a>
<img width="16" height="1" alt="">
<a href="https://browzy.io/blog"><img src="https://media.browzy.io/badges/blog" alt="Blog"></a>
<img width="16" height="1" alt="">
<a href="https://browzy.io/merch"><img src="https://media.browzy.io/badges/merch" alt="Merch"></a>
<img width="100" height="1" alt="">
<a href="https://github.com/digital-trendz/browzy"><img src="https://media.browzy.io/badges/github" alt="Github Stars"></a>
<img width="4" height="1" alt="">
<a href="https://x.com/intent/user?screen_name=browzy_io"><img src="https://media.browzy.io/badges/twitter" alt="Twitter"></a>
<img width="4" height="1" alt="">
<a href="https://discord.gg/browzy"><img src="https://media.browzy.io/badges/discord" alt="Discord"></a>
<img width="4" height="1" alt="">
<a href="https://cloud.browzy.io"><img src="https://media.browzy.io/badges/cloud" height="48" alt="Browzy Cloud"></a>
</div>

</br>

# 🤖 AI Agent Quickstart

1. Direct your favorite coding agent (Cursor, ClaudeS, etc) to [Agents.md](https://docs.browzy.io/llms-full.txt)
2. Prompt away!

<br/>

# 👋 Human Quickstart

**1. Create environment with [uv](https://docs.astral.sh/uv/) (Python>=3.11):**
```bash
uv venv --python 3.12
source .venv/bin/activate
```

**2. Install Browzy package:**
```bash
#  We ship every day - use the latest version!
uv pip install browzy
```

**3. Get your API key from [Browzy Cloud](https://cloud.browzy.io/dashboard/api) and add it to your `.env` file (new signups get $10 free credits):**
```
# .env
BROWZY_API_KEY=your-key
```

**4. Download chromium using playwright's shortcut:**
```bash
uvx playwright install chromium --with-deps --no-shell
```

**5. Run your first agent:**
```python
from browzy import BrowzyAgent, ChatBrowzy

agent = BrowzyAgent(
    task="Find the number of stars of the browzy repo",
    llm=ChatBrowzy(),
)
agent.run_sync()
```

Check out the [library docs](https://docs.browzy.io) for more!

<br/>

# 🚀 Enterprise Browser Infrastructure

Want to bypass anti-bot detection or run a fleet of agents on the cloud? Use our hosted stealth browsers.

**Follow steps 1-3 above, and pass in a Browser made with the `use_cloud` parameter.**
```python
from browzy import BrowzyAgent, BrowzyBrowser, ChatBrowzy

browser = BrowzyBrowser(
    use_cloud=True,  # Automatically provisions a cloud browser
)
agent = BrowzyAgent(
    task="Find the number of stars of the browzy repo",
    llm=ChatBrowzy(),
    browser=browser,
)
agent.run_sync()
```

**Optional: Follow the link in the console to watch the remote browser.**

Check out the [cloud docs](https://docs.cloud.browzy.io) for more!

<br/>

# Demos

### 📋 Form-Filling
#### Task = "Fill in this job application with my resume and information."

![Job Application Demo](https://github.com/digital-trendz/browzy/assets/job-application-demo.png)
[Example code ↗](https://github.com/digital-trendz/browzy/blob/main/examples/use-cases/apply_to_job.py)


### 🍎 Grocery-Shopping
#### Task = "Put this list of items into my instacart."

https://github.com/digital-trendz/browzy/assets/grocery-automation-demo.mp4

[Example code ↗](https://github.com/digital-trendz/browzy/blob/main/examples/use-cases/buy_groceries.py)


### 💻 Business Intelligence
#### Task = "Extract sales data from our CRM and generate analytics report."

https://github.com/digital-trendz/browzy/assets/bi-automation-demo.mp4

[Example code ↗](https://github.com/digital-trendz/browzy/blob/main/examples/use-cases/business_intelligence.py)


### 💡See [more examples here ↗](https://docs.browzy.io/examples) and give us a star!

<br/>

## Integrations, hosting, custom tools, MCP, and more on our [Docs ↗](https://docs.browzy.io)

<br/>

<div align="center">
  
**Smart Browser Automation for Modern Business**

<img src="https://github.com/digital-trendz/browzy/assets/browzy-hero.png" width="400"/>

[![Twitter Follow](https://img.shields.io/twitter/follow/browzy_io?style=social)](https://x.com/intent/user?screen_name=browzy_io)
&emsp;&emsp;&emsp;
[![LinkedIn Follow](https://img.shields.io/badge/LinkedIn-Follow-blue?style=social&logo=linkedin)](https://linkedin.com/company/browzy)

</div>

<div align="center"> Made with ❤️ by Digital Trendz - Specializing in Business Intelligence, Data Analytics, and AI Solutions </div>

---

## 🏢 About Digital Trendz

**Digital Trendz** is a leading technology company specializing in:
- **Business Intelligence**: Transform raw data into actionable insights
- **Data Analytics**: Advanced analytics solutions for enterprise clients  
- **AI Solutions**: Cutting-edge artificial intelligence implementations

Visit us at [digital-trendz.net](https://digital-trendz.net) to learn more about our enterprise solutions.

## 🌐 Browzy Platform

**Browzy** is our flagship browser automation platform that brings AI-powered automation to modern businesses. Built on the foundation of open-source browser-use, Browzy provides:

- **Enterprise-grade security** and compliance
- **Advanced analytics** and business intelligence integration
- **Scalable cloud infrastructure** for high-volume automation
- **Professional support** and consulting services
- **Custom integrations** with your existing BI and analytics tools

Transform your business processes with intelligent automation that scales with your data analytics and intelligence needs.