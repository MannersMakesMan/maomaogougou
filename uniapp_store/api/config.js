let url = '';
if (process.env.NODE_ENV == 'development') {
	url = 'http://112.74.165.106:8000' //本地地址、测试地址
} else {
	url = 'http://112.74.165.106:8000' //生产环境地址
}

const baseUrl = url
export default baseUrl
