import React, {Component} from 'react';
import { Layout, Menu, theme } from 'antd';
const { Header } = Layout;

class App extends Component {
  render() {
    return (
        <div style={{background: '#fff', width: '100vw', height: '100vh', borderRadius: 10}}>
            <Layout>
                <Header style={{
                    background: '#fff',
                    position: 'sticky',
                    top: 0,
                    zIndex: 1,
                    width: '100%',
                    borderTopLeftRadius: 10,
                    borderTopRightRadius: 10
                }}>
                    <h2>长空御风2023视觉组寒假作业</h2>

                </Header>
            </Layout>
        </div>
    );
  }
}

export default App;
