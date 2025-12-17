# 自动刚体抓握frame标注说明：

自动刚体标注后标注的中心点在刚体的中心位置（从robotwin刚体配套的json文件extents字段获得），标注方向为，标注scale一般采用robotwin的json文件中的scale字段：

<img width="2559" height="1489" alt="image" src="https://github.com/user-attachments/assets/0d3aa7df-e7fb-4c16-8063-8f94ef100395" />

以及：

<img width="2206" height="1183" alt="image" src="https://github.com/user-attachments/assets/3fd7236b-b4ac-4d01-82e0-c53ae229a477" />

## 标注文件脚本说明：

**batch_process_usd**.sh调用一般的auto_label_rigid.py来进行批量标注。

**batch_process_usd_spe**.sh用于对robotwin中的特殊资产（即scale没有在json文件且原本的scale有问题的）进行标注（scale默认设置为(0.1,0.1,0.1)）。

**grasp_labels**.json文件中记载了这类模型文件是否适合抓握，即True of false

**copy_suitable_objects**.py文件实现了从转换后的robotwin刚体文件资产按照grasp_labels.json中拷贝过来适合抓握的文件

**copy_unverified_models**.sh文件把还没有验证的继续拷贝到待验证的目录

## 测试标注文件脚本说明

基于teleillusion的任务实现，通过判断是否能成功的把物体从某个地方移动到指定位置来说明刚体是否是真正适合抓握的，如果真正适合抓握，则会在visual下面和原来usd同文件夹的地方保存一个同名txt文件。

**run_all_rigids**.sh批量测试脚本

## 额外说明

下面的四个robotwin模型文件需要特别的使用batch_process_usd_spe.sh。

031_jam-jar

069_vagetable

"108_block"

"028_roll-paper": false
