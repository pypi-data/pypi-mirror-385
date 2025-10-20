from setuptools import setup, find_packages

setup(
    name="survivor_optimizer",
    version="0.1",
    packages=find_packages(),
    install_requires=["numpy"],  # وابستگی‌ها
    python_requires=">=3.7",
    author="َArif Yelği",          # نویسنده اصلی
    author_email="ar.yelqi@gmail.com",        # ایمیل نویسنده
    maintainer="Shirmohammad Tavangari",                  # نگهدارنده پروژه
    maintainer_email="shmt.researcher@gmail.com",    # ایمیل نگهدارنده
    description="Survivor optimizer: A competitive strategy for enhanced search efficiency",
    url="https://www.sciencedirect.com/science/article/pii/S2090447925003028",
)
