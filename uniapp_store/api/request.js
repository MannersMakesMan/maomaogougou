import Vue from 'vue'

const baseOptions = (params, method = 'GET') => {

	let {
		url,
		data
	} = params
	let contentType = 'application/x-www-form-urlencoded'
	contentType = params.contentType || contentType

	const token = uni.getStorageSync('token')
	return new Promise((resolve, reject) => {
		const option = {
			url: url,
			data: data,
			method: method,
			header: {
				'content-type': contentType,
				'Authorization': token
			},
			success: (res) => {
				console.log(res, option)
				if (!res.data) { // 不存在data数据
					return reject('数据异常!');
				}

				if ('200' === res.data.code) {
					// doToken(res)
					return resolve(res.data);
					console.log(res)
				} else {
					if ('999998' === res.data.code) {
						// 自动登录
						uni.showToast({
							icon: 'none',
							title: res.data.msg
						})
						return reject([res.data.msg, res.data.code]);
					} else if ('500' === res.statusCode) {
						uni.showToast({
							icon: 'none',
							title: res.data.msg
						})
						// Vue.prototype.$store.commit('LOGIN_TIP', true);
						return reject([res.data.msg, res.data.code]);
					} else {
						Vue.prototype.$store.commit('LOGIN_TIP', true);
						return reject(res.data.msg);
					}
				}
			}
		};
		uni.request(option);
	});
}


export const doGet = (url, data = '', contentType) => {
	let option = {
		url,
		data,
		contentType
	}
	return baseOptions(option, 'GET');
}

export const doPost = (url, data = '', contentType) => {
	let params = {
		url,
		data,
		contentType
	};
	return baseOptions(params, 'POST')
}

export const doDelete = (url, data = '', contentType) => {
	let option = {
		url,
		data,
		contentType
	}
	return baseOptions(option, 'DELETE')
}
export const doPut = (url, data = '', contentType) => {
	let option = {
		url,
		data,
		contentType
	}
	return baseOptions(option, 'PUT')
}

export const doPostJson = (url, data = '') => {
	return doPost(url, data, 'application/json');
}

export const doGetJson = (url, data = '') => {
	return doGet(url, data, 'application/json');
}

export const doDELETE = (url, data = '') => {
	return doDelete(url, data, 'application/json');
}

export const doPUT = (url, data = '') => {
	return doPut(url, data, 'application/json');
}
