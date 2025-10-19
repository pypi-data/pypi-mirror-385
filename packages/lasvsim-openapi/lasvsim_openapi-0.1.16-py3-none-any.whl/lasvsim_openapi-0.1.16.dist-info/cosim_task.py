
import os

from lasvsim_openapi.client import Client, SimulatorConfig
from lasvsim_openapi.http_client import HttpConfig
from lasvsim_openapi.simulator_model import SimulatorConfig
from lasvsim_openapi.simulator_model import Point


def main():
    # 接口地址和授权token
    endpoint = "http://localhost:8280"
    token = ""

    task_id = int(8)
    record_id = int(30)

    # 1. 初始化客户端
    cli = Client(
        HttpConfig(
            endpoint=endpoint,  # 接口地址
            token=token,  # 授权token
        )
    )

    # 2. 拷贝剧本, 返回的结构中new_record_id字段就是新创建的剧本ID
    # 仿真结束后可到该剧本下查看结果详情
    new_record = cli.process_task.copy_record(task_id, record_id)

    # 3. 通过拷贝的场景Id、Version和SimRecordId初始化仿真器
    simulator = cli.init_simulator_from_config(
        SimulatorConfig(
            scen_id=new_record.scen_id,
            scen_ver=new_record.scen_ver,
            sim_record_id=new_record.sim_record_id,
        )
    )

    try:
        # 获取测试车辆列表
        test_vehicle_list = simulator.get_test_vehicle_id_list()
        
        #获取所有车辆ID列表
        vehicle_list = simulator.get_vehicle_id_list()
        # print("车辆ID",vehicle_list)


        # 记录仿真器运行状态(True: 运行中; False: 运行结束), 任务运行过程中持续更新该状态
        is_running = True

        # 使测试车辆环形行驶
        while is_running:
            # 设置方向盘转角10度, 纵向加速度0.05
            ste_wheel = 0.0
            lon_acc = 0.5


            positin_res = simulator.get_vehicle_position(test_vehicle_list.list)
            position = positin_res.position_dict[test_vehicle_list.list[0]]
            print("自车车辆位置",position.point.y)
            # 设置车辆的控制信息
            # simulator.set_vehicle_planning_info(test_vehicle_list.list[0],planning_path=[position.point,Point(x=position.point.x,y=position.point.y+30,z=position.point.z)],speed=[30.0,30.00])

            moving_info_res = simulator.get_vehicle_moving_info(test_vehicle_list.list)
            moving_info = moving_info_res.moving_info_dict[test_vehicle_list.list[0]]
            # print(moving_info)
           
            # 设置车辆的控制信息
            simulator.set_vehicle_control_info(
                test_vehicle_list.list[0], ste_wheel, lon_acc
            )

            # 执行仿真器步骤
            step_res = simulator.step()
            is_running = step_res.code.is_running()

    finally:
        # 停止仿真器, 释放服务器资源
        simulator.stop()


if __name__ == "__main__":
    main()