import React, {Component} from 'react';
import {Card, Form, Select, Slider, Row, Col, Tooltip, Spin, Statistic, Empty, Space, Result} from "antd";
import {QuestionCircleOutlined } from "@ant-design/icons";

import './border.css'

class Local extends Component {
    state = {mode: 'stupid', size: 3, loading: false, result: null, t: new Date().getTime()}

    formRef = React.createRef()

    onModeChange(mode) {
        this.setState({mode})
    }

    onSizeChange(size) {
        this.setState({size})
    }

    startComputeCreator() {
        const that = this;
        return () => {
            that.setState({loading: true})
            return that.formRef?.current?.getFieldsValue(true)
        }
    }

    finishComputeCreator() {
        const that = this;
        return result => {
            that.setState({loading: false, result, t: new Date().getTime()})
        }
    }

    render() {
        return (
            <div className="content">
                <Card title="参数设置" style={{width: '100%'}} size="small">
                    <Form ref={this.formRef} layout="inline" initialValues={{
                        mode: 'stupid',
                        size: 3,
                        en: 10,
                        pn: 6
                    }}>
                        <Form.Item label="难度" name="mode">
                            <Select
                                style={{width: 90}}
                                onChange={v => this.onModeChange(v)}
                                options={[
                                    {
                                        value: 'stupid',
                                        label: '傻瓜',
                                    },
                                    {
                                        value: 'easy',
                                        label: '简单',
                                    },
                                    {
                                        value: 'normal',
                                        label: '普通',
                                    },
                                    {
                                        value: 'custom',
                                        label: '自定义',
                                    },
                                ]}
                            />
                        </Form.Item>
                        <Form.Item label="尺寸" name="size">
                            <Select
                                disabled={this.state.mode !== 'custom'}
                                style={{width: 80}}
                                onChange={v => this.onSizeChange(v)}
                                options={[
                                    {
                                        value: 3,
                                        label: '3x3',
                                    },
                                    {
                                        value: 4,
                                        label: '4x4',
                                    },
                                    {
                                        value: 5,
                                        label: '5x5',
                                    },
                                    {
                                        value: 6,
                                        label: '6x6',
                                    },
                                ]}
                            />
                        </Form.Item>
                        <Form.Item label="点数" name="pn">
                            <Slider
                                min={this.state.size}
                                max={this.state.size * this.state.size}
                                style={{width: 120}}
                                disabled={this.state.mode !== 'custom'}
                            />
                        </Form.Item>
                        <Form.Item label="边数" name="en">
                            <Slider min={4} max={15} style={{width: 120}} marks={{
                                4: '多',
                                15: '少'
                            }} tooltip={{formatter: null}} disabled={this.state.mode !== 'custom'}/>
                        </Form.Item>
                    </Form>
                </Card>
                <Row style={{paddingTop: 5, paddingBottom: 5}} gutter={5}>
                    <Col span={15}>
                        <Card title="结果" size="small" style={{height: 631, overflow: "hidden"}} >
                            <Spin spinning={this.state.loading} delay={500} size="large">
                                {
                                    this.state.result ?
                                        <div style={{width: '100%', height: 570, margin: 10}}>
                                            <Result
                                                status={this.state.result.ok? "success": "warning"}
                                                title={this.state.result.ok? "解决方案有效": "有一点点问题呢"}
                                            />
                                            <Row>
                                                <Col span={12}>
                                                    <Space direction="vertical" size="middle">
                                                        <Statistic title="时间" value={this.state.result.time} />
                                                        <Statistic title="点查准率" value={this.state.result.np} />
                                                        <Statistic title="点查全率" value={this.state.result.nr} />
                                                    </Space>
                                                </Col>
                                                <Col span={12}>
                                                    <Space direction="vertical" size="middle">
                                                        <Statistic
                                                            title="一笔画"
                                                            value={this.state.result.co ? "成功": "失败"}
                                                        />
                                                        <Statistic title="边查准率" value={this.state.result.ep} />
                                                        <Statistic title="边查全率" value={this.state.result.er} />
                                                    </Space>
                                                </Col>
                                            </Row>
                                        </div> :
                                        <Empty style={{marginTop: 100}} image={Empty.PRESENTED_IMAGE_SIMPLE} />
                                }
                            </Spin>
                        </Card>
                    </Col>
                    <Col span={9}>
                        <Card title="题目" size="small">
                            <div style={{width: "100%", height: 250, overflow: "hidden"}}>
                                {
                                    this.state.result ?
                                        <img src={`/images/question.png?t=${this.state.t}`} alt="question" style={{
                                            width: 250,
                                            height: 250,
                                            alignSelf: 'center'
                                        }}/> :
                                        <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} />
                                }
                            </div>
                        </Card>
                        <Card title="结果可视化" size="small" style={{marginTop: 5}} extra={
                            <Tooltip placement="bottomRight" title={
                                <div>
                                    与原图一致的部分表示查找正确<br />
                                    纯红节点表示这个点在答案中不存在但你输出了<br />
                                    描边较少的节点表示这个节点在答案中但你没找到<br />
                                    灰色边表示这条边在答案中不存在但你输出了<br />
                                    紫色边表示这条边在答案中但你没找到
                                </div>
                            }>
                                <QuestionCircleOutlined />
                            </Tooltip>
                        }>
                            <div style={{width: "100%", height: 250, overflow: "hidden"}}>
                                {
                                    this.state.result ?
                                        <img src={`/images/result.png?t=${this.state.t}`} alt="result" style={{
                                            width: 250,
                                            height: 250,
                                            alignSelf: 'center'
                                        }}/> :
                                        <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} />
                                }
                            </div>
                        </Card>
                    </Col>
                </Row>
            </div>
        );
    }
}

export default Local;