import { Button, Result, Spin, Modal} from "antd";
import React, {Component} from 'react';
import { login, getName } from "./utils";
import './border.css'

class Online extends Component {
    state = {name: null, loading: true, loginLoading: false}

    async login() {
        const that = this
        that.setState({loginLoading: true})
        const code = await login()
        if (code === 0) {
            getName().then(v=>{
                that.setState({name: v, loading: false, loginLoading: false})
            })
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
        getName().then(v=>{
            that.setState({name: v, loading: false, loginLoading: false})
        })
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