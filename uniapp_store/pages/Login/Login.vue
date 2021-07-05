<template>
	<view class="nx-box">
		<image src="../../static/login.png" mode='aspectFit' class="nx-logo"></image>
		<view class="nx-title">LOGO区域</view>
		<view class="nx-form">
			<input class="nx-input" placeholder="请输入用户名" v-model="login.loginName" />
			<input class="nx-input" password placeholder="请输入密码" v-model="login.password" />
			<view class="nx-label" ></view>
			<button class="nx-btn" @tap="loginFunction">立即登录</button>
			<!-- <navigator url="./register" hover-class="none" class="nx-label">还没有账号？点此注册.</navigator> -->
		</view>
	</view>
</template>

<script>
	import {
		doLogin,
		userinfo
	} from '../../api/modules/login.js'

	export default {
		onShow() {

		},
		data() {
			return {
				login: {
					loginName: 'admin2', //手机号码
					password: '' //密码
				},
			};
		},
		methods: {
			// 忘记密码
			onClickPassword() {
				uni.navigateTo({
					url: './register'
				})
			},
			//当前登录按钮操作
			loginFunction() {
				let that = this;
				if (!that.login.loginName) {
					uni.showToast({
						title: '请输入账户',
						icon: 'none'
					});
					return;
				}
				// if (!/^[1][3,4,5,6,7,8,9][0-9]{9}$/.test(that.loginName)) {
				// 	uni.showToast({
				// 		title: '请输入正确手机号',
				// 		icon: 'none'
				// 	});
				// 	return;
				// }
				if (!that.login.password) {
					uni.showToast({
						title: '请输入密码',
						icon: 'none'
					});
					return;
				}
				doLogin({
					password: this.login.password,
					username: this.login.loginName
				}).then(res => {
					console.log(res)
					if (res.code == '200') {
						uni.setStorageSync('token', res.data.HTTP_AUTHORIZATION)
						this.userinfo(res.data.HTTP_AUTHORIZATION)
					} else {
						console.log(1)
						uni.showToast({
							icon: 'none',
							title: '登录失败'
						})
					}

				})
				// this.$apis.postLogin(this.login).then(res => {
				// 	uni.showToast({
				// 		title: '登录成功！',
				// 		icon: 'none'
				// 	});
				// 	that.$store.commit("SET_TOKEN", res.token);

				// });
			},
			// 获取用户信息
			userinfo(token) {
				userinfo({
					AUTHORIZATION: token
				}).then(res => {
					if (res.code == '200') {
						uni.showToast({
							icon: 'none',
							title: '登录成功'
						})
						this.$store.commit('USER_INFO', res.data)
						this.$store.commit('LOGIN_TIP', false)
						setTimeout(() => {
							uni.switchTab({
								url: '../index/index'
							})
						}, 500)
					} else {
						uni.showToast({
							icon: 'none',
							title: '登录失败'
						})
					}
				})
			}
		}
	}
</script>

<style scoped>
	.nx-box {
		padding: 0 100upx;
		position: relative;
	}

	.nx-logo {
		width: 100%;
		width: 100%;
		height: 310upx;
	}

	.nx-title {
		position: absolute;
		top: 0;
		line-height: 360upx;
		font-size: 68upx;
		color: #fff;
		text-align: center;
		width: 100%;
		margin-left: -100upx;
	}

	.nx-form {
		margin-top: 300upx;
	}

	.nx-input {
		background: #e2f5fc;
		margin-top: 30upx;
		border-radius: 100upx;
		padding: 20upx 40upx;
		font-size: 36upx;
		box-sizing: content-box;
	}


	.nx-label {
		padding: 60upx 0;
		text-align: center;
		font-size: 30upx;
		color: #a7b6d0;
	}

	.nx-btn {
		background: #ff65a3;
		color: #fff;
		border: 0;
		border-radius: 100upx;
		font-size: 36upx;
	}

	.nx-btn:after {
		border: 0;
	}

	/*按钮点击效果*/
	.nx-btn.button-hover {
		transform: translate(1upx, 1upx);
	}
</style>
