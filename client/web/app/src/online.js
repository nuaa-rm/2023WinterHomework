import { Button, Result, Spin, Modal } from "antd";
import React, {Component} from 'react';
import { login, initClient } from "./utils";
import './border.css'

class Online extends Component {
    state = {name: null, loading: true, loginLoading: false}

    async login() {
        const that = this
        that.setState({loginLoading: true})
        Modal.info({
            title: '请在打开的浏览器窗口中完成登陆',
            content: (
                <div>
                    如果浏览器窗口没有正常打开，请在终端中复制链接后到浏览器中打开
                </div>
            )
        })
        const code = await login()
        if (code === 0) {
            try {
                initClient().then(v=>{
                    if (v.td > 5) {
                        Modal.error({
                            title: '出错啦',
                            content: '本地时间与服务器时间相差过多，请重新同步时间'
                        })
                    } else {
                        Modal.destroyAll()
                        that.setState({name: v.name, loading: false, loginLoading: false})
                    }
                })
            } catch (_) {
                Modal.error({
                    title: '出错啦',
                    content: '程序运行时出现错误'
                })
            }
        } else if (code === 11) {
            Modal.error({
                title: '出错啦！',
                content: '操作超时'
            })
            that.setState({loginLoading: false})
        }
    }

    componentDidMount() {
        const that = this
        try {
            initClient().then(v=>{
                if (v.td > 5) {
                    Modal.error({
                        title: '出错啦',
                        content: '本地时间与服务器时间相差过多，请重新同步时间'
                    })
                } else {
                    that.setState({name: v.name, loading: false, loginLoading: false})
                }
            })
        } catch (_) {
            Modal.error({
                title: '出错啦',
                content: '程序运行时出现错误'
            })
        }
    }

    render() {
        return (
            <div className="content">
                {
                    this.state.loading ?
                        <div style={{paddingTop: 150, textAlign: 'center'}}>
                            <Spin tip="加载中..." size="large" />
                        </div> :
                        (
                            this.state.name ?
                                <div style={{paddingTop: 150, textAlign: 'center'}}>
                                    <h1>欢迎，{this.state.name}</h1>
                                    <h2>本功能其他部分正在开发中</h2>
                                </div> :
                                <Result
                                    status="info"
                                    title="您还没有登陆"
                                    extra={
                                        <Button
                                            type="primary"
                                            size="large"
                                            loading={this.state.loginLoading}
                                            onClick={()=>this.login()}
                                        >
                                            立即登陆
                                        </Button>
                                    }
                                />
                        )
                }
            </div>
        );
    }
}

export default Online;