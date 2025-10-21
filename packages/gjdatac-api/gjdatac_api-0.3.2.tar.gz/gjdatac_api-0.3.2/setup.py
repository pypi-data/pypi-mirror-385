from setuptools import setup, find_packages

with open('description_info.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gjdatac_api',  # 你的包名
    version='0.3.2',  # 版本号
    description='数据接口打包',  # 包的简要描述
    long_description=long_description,  # 包的详细描述
    long_description_content_type='text/markdown',  # 描述文件的类型
    include_package_data=True,  # 包含包数据
    package_data={'gjdatac_api': ['*.py', 'dict_data.py', 'dolphindb_info.py', 'instrument_class.py','data_api_class.py']},  # 指定数据文件
    author='fml',  # 作者姓名
    author_email='13306510996@163.com',  # 作者邮箱
    packages=find_packages(),  # 自动查找包目录
    python_requires='>3.6',  # python版本要求
    install_requires=[
        'dolphindb==3.0.1.0',
        'holidays==0.53',
        'numpy==1.26.3',
        'pandas==2.2.0',
        'chinese_calendar==1.10.0'
    ],  # 依赖库列表 (除开python自带的包外的其他依赖库(代码中如果缺少了对应的库会导致无法运行的包))
)
