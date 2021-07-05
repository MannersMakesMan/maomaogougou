<template>
	<view class="aui-flexView">
		<view class="seh-box seh-box-w">
			<view class="serach aSearch-input-box">
				<view class="content" style="border-radius: 60px;">
					<view class="content-box">
						<input :placeholder="defaultKw" confirm-type="search" class="input" v-model="inputVal" />
					</view>
					<view class="serachBtn" @click="doSearch">
						搜索
					</view>
				</view>
			</view>
		</view>
		<view class="aui-scrollView">
			<view class="tab-item" v-for="(item,index) in newsList" :key="index" @click="onClickDetail(item)">
				<a class="aui-well-item aui-well-item-clear">
					<view class="aui-well-item-bd">
						<h3>订单号：{{item.order_number}}</h3>
					</view>
					<span class="aui-well-item-fr">{{item.create_time}}</span>
				</a>
				<view class="aui-mail-product" v-for="(list,keys) in item.goods_data" :key="keys">
					<view href="javascript:;" class="aui-mail-product-item">
						<view class="aui-mail-product-item-hd">
							<image :src="showImg(list.sku.default_image_url)" mode=""></image>
						</view>
						<view class="aui-mail-product-item-bd">
							<view class="f1">{{list.sku.name}}</view>
							<view class="">
								<text
									style="font-size: 22rpx;padding-top: 10rpx;color: red;font-weight: bold;">{{list.price}}</text>￥
							</view>
							<view class="" style="font-size: 22rpx;">
								x{{list.count}}
							</view>
						</view>
					</view>
				</view>
				<view href="javascript:;" class="aui-mail-payment">
					<view>
						共{{item.goods_data.length}}件商品 实付款: ￥{{item.total_amount}}
					</view>
				</view>

			</view>
			<tui-loadmore :visible="loadding" :index="3" type="red"></tui-loadmore>
			<tui-nomore :visible="!pullUpOn"></tui-nomore>
		</view>
		<!-- 登录弹框 -->
		<shopro-login-modal></shopro-login-modal>
	</view>
</template>

<script>
	import {
		orderOperate
	} from '../../api/modules/login.js'
	import baseUrl from '../../api/config.js'

	export default {
		data() {
			return {
				defaultKw: '请输入店铺名',
				inputVal: '',
				loadding: false,
				pullUpOn: true,
				PageIndex: 1,
				PageSize: 10,
				newsList: []
			};
		},
		// 上拉加载
		async onReachBottom() {
			if (!this.pullUpOn) return;
			this.PageIndex = this.PageIndex + 1;
			this.loadding = true;

			this.orderOperate()
		},
		onLoad() {
			this.orderOperate()
		},
		methods: {
			onClickDetail(item) {
				uni.navigateTo({
					url: './Detail?item=' + JSON.stringify(item)
				})
			},
			// 搜索
			doSearch() {
				this.orderOperate()
			},
			// 订单
			orderOperate() {
				let params = {
					page: this.PageIndex,
					page_size: this.PageSize,
					query_type: 1,
					client_name: this.inputVal
				}
				orderOperate(params).then(res => {
					if (res.code == '200') {
						if (!res.data.data || res.data.data.length < this.PageSize) {
							this.pullUpOn = false;
						}
						this.loadding = false;
						if (this.PageIndex == 1) {
							this.newsList = res.data.data
						} else {
							this.newsList = this.newsList.concat(res.data.data)
						}
					}
				})
			},
			showImg(img) {
				return baseUrl + img
			}
		}
	}
</script>

<style lang="less">
	.tab-item{
		width: 690rpx;
		background-color: #fff;
		margin: 0 auto;
	}
	.addBtn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 100rpx;
		height: 100rpx;
		border-radius: 50%;
		background-color: rgba(80, 212, 212);
		color: #fff;
		font-size: 22rpx;
		position: fixed;
		right: 5%;
		bottom: 5%;
	}

	.item-box {
		width: 550rpx;
		padding-bottom: 20rpx;
		margin: 0 auto;
		background-color: #fff;
		border: 1px solid #F5F5F5;
		border-radius: 20rpx;

		.item-name {
			font-size: 22rpx;
			color: #333;
			font-weight: bold;
			padding: 20rpx;
			// border-bottom: 1rpx solid #DDDDDD;
		}
	}

	.content {
		display: flex;
		align-items: center;
		width: 100%;
		height: 60upx;
		//border: 1px #ccc solid; // 去掉边框
		background: #fff;
		overflow: hidden;
		transition: all 0.2s linear;
		border-radius: 30px;

	}

	.seh-box {
		// width: 100%;
		background-color: rgb(242, 242, 242);

		display: flex;
		justify-content: space-between;
		position: sticky;
		top: 0;
		border: 1rpx solid #efefef;
	}

	.serachBtn {
		height: 100%;
		flex-shrink: 0;
		padding: 0 30upx;
		//按钮背景色
		//background: linear-gradient(to right, #ff9801, #ff570a);
		//background: $uni-color-success;
		line-height: 60upx;
		color: #fff;
		//border-left: 1px #ccc solid; //去掉边框
		transition: all 0.3s;
		background: linear-gradient(to right, rgb(175, 238, 238), rgb(51, 204, 204));
	}


	.content-box {
		width: 100%;
		display: flex;
		align-items: center;


		.input {
			// padding-left: 20upx;
			width: 100%;
			max-width: 100%;
			line-height: 60upx;
			height: 60upx;
			transition: all 0.2s linear;
			font-size: 20rpx;
			padding:10px;
			&.center {
				width: 200upx;
			}

			&.sub {
				// position: absolute;
				width: auto;
				color: grey;
			}
		}
	}

	.serach {
		display: flex;
		width: 100%;
		box-sizing: border-box;
		font-size: 15px;
	}

	.seh-box .aSearch-input-box {
		width: 100%;
	}

	.seh-box-w {
		width: 95%;
		margin: 0 auto;
	}

	.aui-mail-payment {
		padding: 10px 15px;
		position: relative;
		text-align: right;
		font-size: 0.8rem;
		color: #333;
		overflow: hidden;
		display: block;
	}

	.aui-mail-product {
		// background: #f7f7f7;
		padding: 20px;
		position: relative;
		overflow: hidden;
	}

	.aui-mail-product-item {
		/* padding: 15px; */
		position: relative;
		display: -webkit-box;
		display: -webkit-flex;
		display: flex;
		-webkit-box-align: center;
		-webkit-align-items: center;
		align-items: center;
	}

	.aui-mail-product-item-hd {
		margin-right: .8em;
		width: 70px;
		height: 70px;
		line-height: 70px;
		text-align: center;
	}

	.aui-mail-product-item-hd image {
		width: 100%;
		max-height: 100%;
		vertical-align: top;
	}

	.aui-mail-product-item-bd {
		-webkit-box-flex: 1;
		-webkit-flex: 1;
		flex: 1;
		min-width: 0;
	}

	.aui-mail-product-item-bd .f1 {
		color: #404040;
		font-size: 13px;
		line-height: 1.4;
		overflow: hidden;
		text-overflow: ellipsis;
		display: -webkit-box;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 3;
		text-decoration: none;
	}

	/* 必要布局样式css */
	.aui-flexView {
		width: 100%;
		height: 100%;
		margin: 0 auto;
		display: -webkit-box;
		display: -webkit-flex;
		display: -ms-flexbox;
		display: flex;
		-webkit-box-orient: vertical;
		-webkit-box-direction: normal;
		-webkit-flex-direction: column;
		-ms-flex-direction: column;
		flex-direction: column;
	}

	.aui-scrollView {
		width: 100%;
		height: 100%;
		-webkit-box-flex: 1;
		-webkit-flex: 1;
		-ms-flex: 1;
		flex: 1;
		overflow-y: auto;
		overflow-x: hidden;
		-webkit-overflow-scrolling: touch;
		position: relative;
		/* margin-top: -44px; */
	}

	.aui-well-item {
		padding: 20rpx;
		position: relative;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.aui-well-item-hd {
		margin-right: .4em;
		width: 19px;
		height: 19px;
		line-height: 19px;
		text-align: center;
	}

	.aui-well-item-hd image {
		width: 100%;
		max-height: 100%;
		vertical-align: top;
		display: block;
		border: none;
		margin-top: 3px;
	}

	.aui-well-item-bd {
	
	}

	.aui-well-item-bd h3 {
		color: #333;
		font-size: 0.9rem;
		position: relative;
		/* padding-left: 20px; */
		font-weight: normal;
		padding-bottom: 0;
		text-align: left;
		width: 300rpx;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.aui-well-item-fr {
		font-size: 0.85rem;
		text-align: right;
		color: #999999;
		padding-right: 25px;
		position: relative;
	}
</style>
