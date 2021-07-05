<template>
	<view class="page_box">
		<view class="" style="padding: 20rpx;">
			<uni-combox label="店铺名" labelWidth="150px" @inputId="onClickInputId" :itemData="itemData"
				@input="onClickinput" placeholder="请输入店铺名查找" v-model="city"></uni-combox>
			<view class="example-body">
				<combox-search label="送达时间" labelWidth="100px" emptyTips="无匹配选项" :isJSON="true" :keyName="keyName"
					:candidates="candidates" placeholder="请选择送达时间" :labelWidth="'150px'"
					@getValue="getValue($event,'json')">
				</combox-search>
			</view>
		</view>
		<view class="content_box">
			<view class="goods-list">
				<view class="goods-card" v-for="(item,index) in goods_info" :key="index">
					<view class="goods-box x-start">
						<view class="">
							<image :src="item.goods_img" class="goods-img" mode=""></image>
						</view>
						<view class="y-start">
							<view class="goods-title more-t">
								{{item.goods_name}}
							</view>
							<view class="size-tip">

							</view>
							<view class="goods-price x-bc">
								<view class="">
									￥{{item.goods_price}}
								</view>
								<view class="goods-num">
									x{{item.goods_num}}
								</view>
							</view>
						</view>
					</view>
				</view>
			</view>
			<!-- <view class=" x-bc item-list border-top">
				<view class="item-title">商品金额</view>
				<view class="x-f">
					<text class="price">￥1</text>
				</view>
			</view>
			<view class="price-box x-bc item-list">
				<view class="item-title">运费</view>
				<view class="x-f">
					<text class="price">x 1</text>
				</view>
			</view> -->
		</view>
		<view class="foot_box x-f">
			<text class="num">共1件</text>
			<view class="all-money">
				<text>合计：</text>
				<text class="price">￥{{totle_price}}</text>
			</view>
			<button class="cu-btn sub-btn" @tap="subOrder" :disabled="isSubOrder">
				<text v-if="isSubOrder" class="cuIcon-loading2 cuIconfont-spin"></text>
				提交订单
			</button>
		</view>
		<!-- 登录弹框 -->
		<shopro-login-modal></shopro-login-modal>
	</view>
</template>

<script>
	import uniCombox from '../../components/uni-combox/uni-combox.vue'
	import comboxSearch from "@/components/cuihai-combox/cuihai-combox.vue"
	import {
		getClientSelectLs,
		addOrderOperate,
		getCommonDataForm
	} from '../../api/modules/login.js'

	export default {
		components: {
			uniCombox,
			comboxSearch
		},
		data() {
			return {
				city: '',
				itemData: [],
				isSubOrder: false,
				AreaId: 0,
				goods_info: [],
				keyName: 'name',
				candidates: [],
				totle_price: 0,
				order_type: 0,
				currentIndex: -1
			};
		},
		onLoad(data) {
			this.order_type = data.order_type
			this.goods_info = JSON.parse(data.goods_info)
			this.getCommonDataForm()
			let totalNum = 0
			let totalPrice = 0
			this.goods_info.filter(item => {
				totalNum += 1;
				totalPrice += item.goods_num * Number(item.goods_price)
			})
			this.totle_price = data.totle_price == '0.00' ? totalPrice : data.totle_price
			console.log(totalPrice)
			console.log(this.goods_info)
		},
		methods: {
			getValue(e) {
				this.currentIndex = e
			},
			// 获取公共参数
			getCommonDataForm() {
				getCommonDataForm({
					query_type: 'delivery'
				}).then(res => {
					if (res.code == '200') {
						this.candidates = res.data.delivery_ls
					}
				})
			},
			subOrder() {
				if (this.AreaId != 0) {
					this.isSubOrder = true
					let params = {}
					if (this.order_type == '1') {
						var arr = []
						arr = this.goods_info.map(item => {
							return {
								count: item.goods_num,
								sku: item.goods_id
							}
						})
						params = {
							client_id: this.AreaId,
							goods_data_list: arr,
							delivery_type:this.candidates[this.currentIndex].id,
							order_type: this.order_type
						}
					} else {
						var arr = []
						arr = this.goods_info.map(item => {
							return item.goods_id
						})
						params = {
							client_id: this.AreaId,
							shop_rtolley_ids: arr,
							delivery_type:this.candidates[this.currentIndex].id,
							order_type: this.order_type
						}

					}
					addOrderOperate(params).then(res => {
						if (res.code == '200') {
							this.isSubOrder = false;
							uni.showToast({
								icon: 'none',
								title: '下单成功'
							})
							setTimeout(() => {
								uni.navigateTo({
									url: './List'
								})
							}, 200)
						} else {
							this.isSubOrder = false;
							uni.showToast({
								icon: 'none',
								title: '提交失败'
							})
						}
					})
				} else {
					uni.showToast({
						icon: 'none',
						title: '请选择客户'
					})
				}

			},
			onClickinput(e) {
				console.log(e)
				getClientSelectLs({
					name: e
				}).then(res => {
					this.itemData = res.data.data
				})
			},
			onClickInputId(e) {
				this.AreaId = e
				console.log(e)
			}
		}
	}
</script>

<style lang="less">
	.foot_box {
		height: 100rpx;
		padding: 0 25rpx;
		justify-content: flex-end;
		background-color: #fff;

		.num {
			font-size: 26rpx;
			color: #999;
		}

		.all-money {
			margin: 0 60rpx 0 20rpx;

			.price {
				color: #e1212b;
			}
		}

		.sub-btn {
			width: 210rpx;
			height: 70rpx;
			background: linear-gradient(90deg, rgba(233, 180, 97, 1), rgba(238, 204, 137, 1));
			box-shadow: 0px 7rpx 6rpx 0px rgba(229, 138, 0, 0.22);
			border-radius: 35rpx;
			font-size: 28rpx;
			color: #fff;
		}
	}

	.logistic,
	.price-box,
	.remark-box,
	.score,
	.coupon {
		border-top: 1rpx solid rgba(#dfdfdf, 0.5);
	}

	.border-top {
		border-top: 1rpx solid rgba(#dfdfdf, 0.5);
	}

	.item-list {
		height: 100rpx;
		background: #fff;
		padding: 0 25rpx;

		.item-title {
			font-size: 28rpx;
			margin-right: 20rpx;
		}

		.detail {
			font-size: 28rpx;
			color: #333;
		}

		.price {
			font-size: 26rpx;
			color: #e1212b;
			margin-right: 20rpx;
		}

		.sel-coupon {
			font-size: 26rpx;
			color: #c4c4c4;
			margin-right: 20rpx;
		}

		.cuIcon-right {
			color: #c4c4c4;
		}
	}

	.goods-box {
		position: relative;

		.goods-img {
			height: 180rpx;
			width: 180rpx;
			background-color: #ccc;
			margin-right: 25rpx;
		}

		.order-goods__tag {
			position: absolute;
			top: 0;
			left: 0;
			z-index: 5;

			.tag-img {
				width: 60rpx;
				height: 30rpx;
			}
		}

		.goods-title {
			font-size: 28rpx;
			font-family: PingFang SC;
			font-weight: 500;
			color: rgba(51, 51, 51, 1);
			width: 450rpx;
			line-height: 40rpx;
			margin-bottom: 10rpx;
		}

		.size-tip {
			line-height: 40rpx;
			// background: #f4f4f4;
			// padding: 0 16rpx;
			font-size: 24rpx;
			color: #666;
		}

		.sub-tip {
			width: 480rpx;
			line-height: 40rpx;
			// background: #F6F2EA;
			font-size: 24rpx;
			color: #a8700d;
			margin: 10rpx 0;
		}

		.price {
			color: #e1212b;
		}
	}

	// order
	.goods-box {
		.order-right {
			height: 180rpx;
		}

		.order-tip {
			font-size: 24rpx;
			font-family: PingFang SC;
			font-weight: 400;
			color: rgba(153, 153, 153, 1);
			width: 450rpx;
			margin-bottom: 20rpx;

			.order-num {
				margin-right: 10rpx;
			}
		}

		.order-goods {
			width: 480rpx;

			.status-btn {
				background: none;
				height: 32rpx;
				border: 1rpx solid rgba(207, 169, 114, 1);
				border-radius: 15rpx;
				font-size: 20rpx;
				font-family: PingFang SC;
				font-weight: 400;
				color: rgba(168, 112, 13, 1);
				padding: 0 10rpx;
				margin-left: 20rpx;
				background: rgba(233, 183, 102, 0.16);
			}

			.order-price {
				font-size: 26rpx;
				font-family: PingFang SC;
				font-weight: 600;
				color: rgba(51, 51, 51, 1);
			}
		}
	}

	// 商品卡片
	.goods-list {
		background: #fff;
		position: relative;
		margin-top: 20rpx;

		/deep/ .goods-title {
			width: 460rpx !important;
		}

		.goods-card {
			padding: 30rpx;
		}

		.goods-price {
			font-size: 30rpx;
			font-weight: 500;
			width: 480rpx;

			.goods-num {
				font-size: 28rpx;
				color: #c4c4c4;
			}
		}
	}

	// 商品卡片
	.goods-list {
		background: #fff;
		position: relative;
		margin-top: 20rpx;

		/deep/ .goods-title {
			width: 460rpx !important;
		}

		.goods-card {
			padding: 30rpx;
		}

		.goods-price {
			font-size: 30rpx;
			font-weight: 500;
			width: 480rpx;

			.goods-num {
				font-size: 28rpx;
				color: #c4c4c4;
			}
		}
	}
</style>
