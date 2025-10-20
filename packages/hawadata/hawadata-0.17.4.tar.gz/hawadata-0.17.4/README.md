# 文档

## 说明

1. 用于 Hawa 相关的所有服务的统一数据计算（避免重复计算）。

## 依赖

- Python 3.10+

## 流程
### 1. 初始化配置文件
1. 设置MySQL数据库
2. 设置Redis数据库
3. 设置MongoDB数据库
4. 设置 COMPLETED True
````
set_project() # 参数见文档
# or
set_project(build_set_project_params(project))

````
### 2. 启动服务
1. 启动MongoDB数据库
```` 
.connect()
````

### 3. 使用
````
# 学校报告数据
data = SchoolHealthReportData(**{"meta_unit_id": 3707030003, "target_year": 2021})
# mht web 数据
data = SchoolMhtWebData(**{"meta_unit_id": 4107110001, "target_year": 2022})
````


## 版本