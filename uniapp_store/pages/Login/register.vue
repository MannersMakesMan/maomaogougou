<template>
	<view class="nx-box">
		<image src="../../static/login.png" mode='aspectFit' class="nx-logo"></image>
		<view class="nx-title">LOGO区域</view>
		<view class="nx-form">
			<input class="nx-input"  v-model="password" placeholder="请输入旧密码" />
			<input class="nx-input"  password v-model="new_password" placeholder="请输入新密码" />
			<input class="nx-input"  password v-model="re_password" placeholder="请再输入一次新密码" />
			<button class="nx-btn" @click="onClickPassword">更改密码</button>
			<navigator url="./Login" open-type='navigateBack' hover-class="none" class="nx-label">已有账号，点此去登录.
			</navigator>
		</view>
	</view>
</template>

<script>
	import {
		changePassword
	} from '../../api/modules/login.js'
	export default {
		data() {
			return {
				new_password: null,
				password: null,
				re_password: null
			}
		},
		methods: {
			// 更改密码
			onClickPassword() {
				if (this.new_password && this.password && this.re_password) {
					let params = {
						new_password: this.new_password,
						password: this.password,
						re_password: this.re_password
					}
					changePassword(params).then(res => {
						if (res.code == '200') {
							uni.showToast({
								icon: 'none',
								title: '修改成功'
							})
							setTimeout(() => {
								uni.navigateBack({
									delta: 1
								})
							}, 500)
						}
					})
				} else {
					uni.showToast({
						icon: 'none',
						title: '请输入对应的内容'
					})
				}

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

	.input-placeholder,
	.nx-input {
		color: #94afce;
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
		margin-top: 60upx;
	}

	.nx-btn:after {
		border: 0;
	}

	/*按钮点击效果*/
	.nx-btn.button-hover {
		transform: translate(1upx, 1upx);
	}
</style>
