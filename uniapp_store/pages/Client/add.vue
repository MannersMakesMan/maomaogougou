<template>
	<view class="container">
		<form @submit="formSubmit" @reset="formReset">
			<!-- <tui-list-cell :hover="false">
				<view class="tui-line-cell">
					<view class="tui-title">客户姓名</view>
					<input placeholder-class="tui-phcolor" v-model="peopleName" class="tui-input" placeholder="请输入姓名"
						maxlength="50" type="text" />

				</view>
			</tui-list-cell> -->
			<tui-list-cell>
				<view class="tui-line-cell">
					<view class="tui-title">客户性质</view>
					<radio-group class="radio-group" name="sex" @change="onValue">
						<label class="tui-radio">
							<radio value="1" color="#5677fc" />潜在客户
						</label>
						<label class="tui-radio">
							<radio value="2" color="#5677fc" />有效客户
						</label>
					</radio-group>
				</view>

			</tui-list-cell>
			<!-- <tui-list-cell :hover="true">
				<view class="tui-line-cell">
					<view class="tui-title">微信号</view>
					<input placeholder-class="tui-phcolor" v-model="v_chart_number" class="tui-input"
						placeholder="请输入微信号" maxlength="50" type="text" />
				</view>
			</tui-list-cell> -->
			<tui-list-cell :hover="false">
				<view class="tui-line-cell">
					<view class="tui-title">联系方式</view>
					<input placeholder-class="tui-phcolor" v-model="phone" class="tui-input" name="mobile"
						placeholder="请输入联系方式" maxlength="50" type="number" />
				</view>
			</tui-list-cell>
			<tui-list-cell :hover="false">
				<view class="tui-line-cell">
					<view class="tui-title">店铺名</view>
					<input placeholder-class="tui-phcolor" v-model="shop_name" class="tui-input" name="email"
						placeholder="请输入店铺名" maxlength="50" type="text" />
				</view>
			</tui-list-cell>
			<tui-list-cell :hover="false">
				<view class="" style="flex-direction: column;">
					<view class="tui-title" style="padding-bottom: 20rpx;">详细地址</view>
					<textarea value="" class="text-ff" v-model="textAreaValue" placeholder="请输入详细地址" />
				</view>
			</tui-list-cell>
			<imgUpload @obtain_img="obtain_img" :count="1" :header="header" :img_list="image" :url="showImg">
			</imgUpload>
			<tui-list-cell :hover="false" @click="onAddress">
				<view class="" style="display: flex;align-items: center;justify-content: space-between;">
					<view class="">
						地址信息
					</view>
					<view class="" style="display: flex;align-items: center;justify-content: center;">
						<view class="" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;width: 200px;">
							{{address}}
						</view>
						<image src="../../static/right.png" mode="" style="width: 30rpx;height: 30rpx;"></image>
					</view>
				</view>
			</tui-list-cell>
			<tui-list-cell :hover="false">
				<view class="">

					<tui-cascade-selection height="280rpx" activeColor="#EB0909" lineColor="#EB0909"
						checkMarkColor="#EB0909" :itemList="itemList2" request :receiveData="receiveData"
						@complete="complete2" @change="change"></tui-cascade-selection>
				</view>
			</tui-list-cell>


			<view class="tui-btn-box">
				<button class="tui-button-primary" hover-class="tui-button-hover" formType="submit" type="primary"
					@click="onClickBtn">提交</button>
			</view>
		</form>
		<!-- 登录弹框 -->
		<shopro-login-modal></shopro-login-modal>
	</view>
</template>
<script>
	import sunuiUpimg from '../../components/sunui-upimg/sunui-upimg.vue'
	import imgUpload from '../../components/linzq-imgUpload/linzq-imgUpload.vue'
	const form = require("@/common/tui-validation/tui-validation.js")
	import {
		getPositionLs,
		clientOperate,
	} from '../../api/modules/login.js'
	import baseUrl from '../../api/config.js'

	export default {
		components: {
			sunuiUpimg,
			imgUpload
		},
		data() {
			return {
				address: '',
				latitude: 0,
				longitude: 0,
				itemList2: [],
				receiveData: [],
				ArearId: [],
				textAreaValue: '',
				arrValue: [],
				client_type: '',
				peopleName: '',
				phone: '',
				shop_name: '',
				v_chart_number: '',
				id: null,
				image: []
			}
		},
		onLoad(options) {
			if (options.params) {
				uni.setNavigationBarTitle({
					title: '修改客户'
				})
				let obj = JSON.parse(options.params)
				console.log(obj, '啊啊啊啊啊啊啊啊')
				this.address = obj.item.address
				this.phone = obj.item.phone
				this.shop_name = obj.item.shop_name
				this.v_chart_number = obj.item.v_chart_number
				this.textAreaValue = obj.item.store_address
				this.id = obj.item.id
				
				if(typeof obj.item.image == 'string') {
					this.image = [obj.item.image]
				} else {
					this.image = obj.item.image
				}
				console.log(this.image)
				this.client_type = '1'
				this.peopleName = obj.item.name
			} else {
				console.log(2)
			}
			this.onAddressCity()
		},
		computed: {
			showImg() {
				return baseUrl + '/product/imageManage?type=' + 1
			},
			header() {
				return {
					'Authorization': uni.getStorageSync('token')
				}
			}
		},
		methods: {
			obtain_img(data) {
				this.image = data
				console.log(data, "获取到的图片组" + data.length + "张")
			},
			// 客户性质
			onValue(e) {
				this.client_type = e.detail.value
			},
			// 点击提交
			onClickBtn() {
				// console.log(this.arrValue)
				// var arr = []
				// arr = this.arrValue.map(item => {
				// 	return item.value
				// })
				// console.log(arr)
				// if (!this.id) {
				// 	if (this.textAreaValue != '' && this.address != '' && this.arrValue.length != 0) {
				// 		let params = {
				// 			address: this.address,
				// 			optionsValue: arr,
				// 			client_type: this.client_type,
				// 			latitude: this.latitude,
				// 			longitude: this.longitude,
				// 			name: this.peopleName,
				// 			phone: this.phone,
				// 			shop_name: this.shop_name,
				// 			store_address: this.textAreaValue,
				// 			v_chart_number: this.v_chart_number,
				// 			image: this.image[0]
				// 		}
				// 		clientOperate(params).then(res => {
				// 			if (res.code == '200') {
				// 				setTimeout(() => {
				// 					uni.navigateBack({
				// 						delta: 1
				// 					})
				// 				}, 500)
				// 			}
				// 		})
				// 	} else {
				// 		uni.showToast({
				// 			icon: 'none',
				// 			title: '请选择对应的内容'
				// 		})
				// 	}
				// } else {
				// 	console.log(12)
				// 	if (this.textAreaValue != '' && (this.address != '' && this.address) && this.arrValue.length != 0) {
				// 		let params = {
				// 			id: this.id,
				// 			address: this.address,
				// 			optionsValue: arr,
				// 			client_type: this.client_type,
				// 			latitude: this.latitude,
				// 			longitude: this.longitude,
				// 			name: this.peopleName,
				// 			phone: this.phone,
				// 			shop_name: this.shop_name,
				// 			store_address: this.textAreaValue,
				// 			image: this.image[0],
				// 			v_chart_number: this.v_chart_number
				// 		}
				// 		clientOperate(params).then(res => {
				// 			if (res.code == '200') {
				// 				setTimeout(() => {
				// 					uni.navigateBack({
				// 						delta: 1
				// 					})
				// 				}, 500)
				// 			}
				// 		})
				// 	} else {
				// 		uni.showToast({
				// 			icon: 'none',
				// 			title: '请选择对应的内容'
				// 		})
				// 	}
				// }

			},
			// 点击进入地址选择
			onAddress() {
				console.log(1111)
				uni.chooseLocation({
					longitude: 112.98626,
					latitude: 28.25591,
					success: (data) => {
						this.address = data.address
						this.latitude = data.latitude
						this.longitude = data.longitude
						console.log('位置名称：' + data.name);
						console.log('详细地址：' + data.address);
						console.log('纬度：' + data.latitude);
						console.log('经度：' + data.longitude);
					}
				});

			},
			complete2(e) {
				console.log(e, 'aaaaaaa');
				this.arrValue = e.result
			},
			change(e) {
				console.log(e);
				/**
				 *   layer: 0  第几级 index
					 src: '/static/images/basic/color.png'
					 subIndex: 2   //当前层级下选中项index
					 subText: '30人'  //选中项数据
					 text: '高一(3)班'
					 value: 103 //选中项value数据
				 * */

				// 模拟请求
				let value = e.value;
				let layer = e.layer;
				if (layer == 2) {
					this.receiveData = [];
				} else {

				}
				uni.showLoading({
					title: '请稍候...'
				});
				getPositionLs().then(res => {
					console.log(res)
					if (res.code == '200') {
						uni.hideLoading();
						switch (layer) {
							case 0:
								getPositionLs({
									super_id: e.value
								}).then(response => {
									if (response.code == '200') {
										this.receiveData = response.data.map(item => {
											return {
												text: item.name,
												value: item.id,
												subText: item.level
											}
										})

									}
								})
								break;
							case 1:
								getPositionLs({
									super_id: e.value
								}).then(data => {
									if (data.code == '200') {
										this.receiveData = data.data.map(item => {
											return {
												text: item.name,
												value: item.id,
												subText: item.level
											}
										})
									}
								})
								break;
						}
					}
				})
				console.log(this.receiveData)
			},
			// 省市区选择
			onAddressCity() {
				getPositionLs().then(res => {
					console.log(res)
					if (res.code == '200') {
						this.itemList2 = res.data.map(item => {
							return {
								text: item.name,
								value: item.id,
								subText: item.level
							}
						})
					}
				})
			},
			formSubmit: function(e) {
				//表单规则
				let rules = [{
					name: "sex",
					rule: ["required"],
					msg: ["请选择客户性质"]
				},{
					name: "mobile",
					rule: ["required", "isMobile"],
					msg: ["请输入联系方式", "请输入正确的联系方式"]
				}, {
					name: "email",
					rule: ["required"],
					msg: ["请输入店铺名"]
				}];
				//进行表单检查
				let formData = e.detail.value;
				let checkRes = form.validation(formData, rules);
				if (!checkRes) {
					console.log(this.arrValue)
					var arr = []
					arr = this.arrValue.map(item => {
						return item.value
					})
					console.log(arr)
					if (!this.id) {
						if (this.textAreaValue != '' && this.address != '' && this.arrValue.length != 0) {
							let params = {
								address: this.address,
								optionsValue: arr,
								client_type: this.client_type,
								latitude: this.latitude,
								longitude: this.longitude,
								// name: this.peopleName,
								phone: this.phone,
								shop_name: this.shop_name,
								store_address: this.textAreaValue,
								// v_chart_number: this.v_chart_number,
								image: this.image[0]
							}
							clientOperate(params).then(res => {
								if (res.code == '200') {
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
								title: '请选择对应的内容'
							})
						}
					} else {
						console.log(12)
						if (this.textAreaValue != '' && (this.address != '' && this.address) && this.arrValue.length !=
							0) {
							let params = {
								id: this.id,
								address: this.address,
								optionsValue: arr,
								client_type: this.client_type,
								latitude: this.latitude,
								longitude: this.longitude,
								// name: this.peopleName,
								phone: this.phone,
								shop_name: this.shop_name,
								store_address: this.textAreaValue,
								image: this.image[0],
								// v_chart_number: this.v_chart_number
							}
							clientOperate(params).then(res => {
								if (res.code == '200') {
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
								title: '请选择对应的内容'
							})
						}
					}
					// uni.showToast({
					// 	title: "验证通过!",
					// 	icon: "none"
					// });
				} else {
					uni.showToast({
						title: checkRes,
						icon: "none"
					});
				}
			},
			formReset: function(e) {
				console.log("清空数据")
			}
		}
	}
</script>

<style lang="less">
	.container {
		padding: 20rpx 0 50rpx 0;
	}

	.tui-line-cell {
		width: 100%;
		box-sizing: border-box;
		display: flex;
		align-items: center;
	}

	.text-ff {
		width: 690rpx;
		height: 150rpx;
		border: 1px solid #DDDDDD;
		font-size: 20rpx;
		padding: 20rpx;
	}

	.tui-title {
		line-height: 32rpx;
		min-width: 120rpx;
		flex-shrink: 0;
	}

	.tui-input {
		font-size: 22rpx;
		color: #333;
		padding-left: 20rpx;
		flex: 1;
		overflow: visible;
	}

	.radio-group {
		margin-left: auto;
		transform: scale(0.8);
		transform-origin: 100% center;
		flex-shrink: 0;
	}

	.tui-radio {
		display: inline-block;
		padding-left: 28rpx;
		font-size: 36rpx;
		vertical-align: middle;
	}


	.tui-btn-box {
		padding: 40rpx 50rpx;
		box-sizing: border-box;
	}

	.tui-button-gray {
		margin-top: 30rpx;
	}

	.tui-tips {
		padding: 30rpx;
		color: #999;
		font-size: 24rpx;
	}
</style>
