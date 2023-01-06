import { LoadingOutlined, WarningOutlined } from '@ant-design/icons';
import { Spin } from 'antd';
import React, {Component} from 'react';

class App extends Component {
    state = {msg: '正在检查更新...', status: 0}

    componentDidMount() {
        const that = this;
        const msgHook = msg => {
            that.setState({msg})
        }

        const statusHook = (status, msg) => {
            that.setState({status, msg})
        }

        window.msgHook = msgHook
        window.statusHook = statusHook
    }

    render() {
        const loadIcon = <LoadingOutlined style={{ fontSize: 64 }} spin />;
        return (
            <div style={{
                position: 'absolute',
                top: '50%',
                marginTop: -84,
                left: '50%',
                marginLeft: -150,
                textAlign: 'center',
                padding: 20,
                paddingTop: 40,
                background: '#fff',
                borderRadius: 10,
                height: 140,
                width: 300
            }}>
                {
                    this.state.status === 0 ?
                        <Spin indicator={loadIcon} />:
                        <WarningOutlined style={{ fontSize: 64, color: "#1677ff" }} />
                }
                <h3 style={{textAlign: 'center', fontSize: 20, color: '#1677ff', width: 300}}>
                    {this.state.msg ? this.state.msg : "loading"}
                </h3>
            </div>
        );
    }
}

export default App;
