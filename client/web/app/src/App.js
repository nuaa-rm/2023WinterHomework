import React, {Component} from 'react';
import {Layout, Button, Tabs, Tooltip} from 'antd';
import {MinusOutlined, CloseOutlined, CaretRightOutlined, GatewayOutlined, PictureOutlined, RedEnvelopeOutlined} from '@ant-design/icons'
import {closeWindow, minimizeWindow, localCompute} from "./utils";
import Local from "./local";
import './border.css'

const {Header} = Layout;

class App extends Component {
    state = {tabKey: 1}

    localTestRef = React.createRef()

    onTabChange = v => {
        this.setState({tabKey: v})
    }

    compute = async () => {
        const that = this
        if (that.state.tabKey === 1) {
            const data = that.localTestRef?.current?.startComputeCreator()()
            console.log(data)
            const result = await localCompute(data)
            that.localTestRef?.current?.finishComputeCreator()(result)
        } else if (that.state.tabKey === 2) {

        } else if (that.state.tabKey === 3) {

        }
    }

    render() {
        return (
            <div className="bbox">
                <Layout style={{borderRadius: 10, width: '100%', height: '100%'}}>
                    <Header className="pywebview-drag-region" style={{
                        background: '#fff',
                        position: 'sticky',
                        top: 0,
                        width: '100%',
                        borderTopLeftRadius: 10,
                        borderTopRightRadius: 10,
                        height: 40,
                        paddingLeft: 60,
                        paddingRight: 10,
                        borderBottom: "2px solid #DEE1E6"
                    }}>
                        <img src={require('./favicon.ico')} alt="logo" height="30px" style={{
                            position: 'absolute',
                            top: 5,
                            left: 20
                        }}/>
                        <h2 style={{
                            position: 'absolute',
                            top: -35,
                            left: 60,
                            color: '#205295',
                            fontFamily: 'YouShe',
                            width: '400px',
                            fontSize: 28,
                            fontWeight: 'normal'
                        }}>
                            长空御风2023视觉组寒假作业
                        </h2>
                        <Button type="text" danger icon={<CloseOutlined/>} style={{
                            float: 'right',
                            marginTop: 5,
                            color: 'black'
                        }} onClick={() => {
                            closeWindow()
                        }}/>
                        <Button type="text" icon={<MinusOutlined/>} style={{
                            float: 'right',
                            marginTop: 5
                        }} onClick={() => {
                            minimizeWindow()
                        }}/>
                    </Header>
                    <Tabs
                        style={{height: '100%', background: '#DEE1E6'}}
                        tabBarStyle={{width: 55}}
                        defaultActiveKey="1"
                        tabPosition="left"
                        type="card"
                        onChange={v=>this.onTabChange(v)}
                        tabBarExtraContent={{
                            left:
                                <Tooltip placement="right" title="运行" >
                                    <Button type="text" icon={<CaretRightOutlined style={{fontSize: 20}} />} style={{
                                        margin: 8
                                    }} onClick={()=>this.compute()}/>
                                </Tooltip>
                        }}
                        items={[
                            {
                                label:
                                    <Tooltip placement="right" title="本地测试" color="blue">
                                        <GatewayOutlined style={{fontSize: 20}} />
                                    </Tooltip>,
                                key: '1',
                                children: <Local ref={this.localTestRef} />,
                            },
                            {
                                label:
                                    <Tooltip placement="right" title="图片输入（开发中）" color="blue">
                                        <PictureOutlined style={{fontSize: 20}} />
                                    </Tooltip>,
                                key: '2',
                                children: `Content of Tab Pane 2`,
                                disabled: true
                            },
                            {
                                label:
                                    <Tooltip placement="right" title="在线红包（开发中）" color="blue">
                                        <RedEnvelopeOutlined style={{fontSize: 20}} />
                                    </Tooltip>,
                                key: '3',
                                children: `Content of Tab Pane 3`,
                                disabled: true
                            },
                        ]}
                    />
                </Layout>
            </div>
        );
    }
}

export default App;
