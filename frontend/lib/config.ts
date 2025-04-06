// 环境变量配置
interface Config {
  apiBaseUrl: string;
  siteUrl: string;
  siteName: string;
}

const config: Config = {
  // API基础URL，生产环境使用ultraquanai.top，开发环境使用localhost
  apiBaseUrl: process.env.NODE_ENV === 'production' 
    ? 'https://ultraquanai.top/api/v1'
    : 'http://localhost:8000/api/v1',
  
  // 站点URL
  siteUrl: process.env.NODE_ENV === 'production'
    ? 'https://ultraquanai.top'
    : 'http://localhost:3000',
  
  // 站点名称
  siteName: 'UltraQuant AI'
};

export default config; 