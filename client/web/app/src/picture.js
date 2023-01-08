import React, {Component} from 'react';
import { Row, Col, Card, Space, Button, Empty } from "antd";
import { LeftOutlined, RightOutlined } from "@ant-design/icons";
import { stepCompute } from "./utils";
import './border.css'

class Picture extends Component {
    state = {nowStep: 0, maxStep: 0, t1: new Date().getTime(), t2: new Date().getTime(), loading: false}

    startComputeCreator() {
        const that = this;
        return async () => {
            that.setState({loading: true})
            const maxStep = await stepCompute()
            that.setState({maxStep, nowStep: 0, t1: new Date().getTime(), loading: false})
        }
    }

    errorHandleCreator() {
        const that = this;
        return async () => {
            that.setState({maxStep: 0, nowStep: 0, t1: new Date().getTime(), loading: false})
        }
    }

    lastStep() {
        const nowStep = this.state.nowStep - 1
        if (nowStep >= 0) {
            this.setState({nowStep, t2: new Date().getTime()})
        }
    }

    nextStep() {
        const nowStep = this.state.nowStep + 1
        if (nowStep <= this.state.maxStep) {
            this.setState({nowStep, t2: new Date().getTime()})
        }
    }

    render() {
        return (
            <div className="content">
                <Row gutter={5} style={{width: '100%', height: '100%'}} >
                    <Col span={12} style={{width: '100%', height: '100%'}} >
                        <Card
                            title="输入图片"
                            size="small"
                            loading={this.state.loading}
                            style={{width: '100%', height: '100%'}}
                        >
                            {
                                this.state.maxStep === 0 ?
                                    <Empty style={{marginTop: 100}} image={Empty.PRESENTED_IMAGE_SIMPLE} /> :
                                    <img
                                        src={`/images/input.png?t=${this.state.t1}`}
                                        alt="input-img"
                                        align="center"
                                        width="100%"
                                    />
                            }
                        </Card>
                    </Col>
                    <Col span={12} style={{width: '100%', height: '100%'}} >
                        <Card
                            title="计算结果"
                            size="small"
                            loading={this.state.loading}
                            style={{width: '100%', height: '100%'}}
                            extra={
                                <Space >
                                    <Button
                                        type="default"
                                        size="small"
                                        onClick={()=>{this.lastStep()}}
                                        disabled={this.state.nowStep <= 0}
                                    >
                                        <LeftOutlined />
                                    </Button>
                                    <Button
                                        type="primary"
                                        size="small"
                                        onClick={()=>{this.nextStep()}}
                                        disabled={this.state.nowStep >= this.state.maxStep}
                                    >
                                        <RightOutlined />
                                    </Button>
                                </Space>
                            }
                        >
                            {
                                this.state.maxStep === 0 ?
                                    <Empty style={{marginTop: 100}} image={Empty.PRESENTED_IMAGE_SIMPLE} /> :
                                    <img
                                        src={`/images/output${this.state.nowStep}.png?t=${this.state.t2}`}
                                        alt="output-img"
                                        align="center"
                                        width="100%"
                                    />
                            }
                        </Card>
                    </Col>
                </Row>
            </div>
        );
    }
}

export default Picture;