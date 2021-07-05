import API from '../api';
import {
	doGet,
	doPost,
	doPostJson,
	doGetJson,
	doDELETE,
	doPUT
} from '../request'

API.extend({
	'/auth/Login': '/manage_account/login', // 登录/注册
	'/auth/userinfo': '/manage_account/userinfo', // 用户信息
	'/auth/GoodsList': '/product/GoodsList', // 商品分类
	'/auth/shopCartUpdate': '/product/shopCartUpdate', // 加入购物车
	'/auth/shopCartList': '/product/shopCartList', // 购物车列表
	'/auth/shopCartUpdates': '/product/shopCartUpdate', // 购物车删除
	'/auth/shopCartUpdateNum': '/product/shopCartUpdate', // 购物车数量
	'/auth/getPositionLs': '/client/getPositionLs', // 省市区
	'/auth/clientOperate': '/client/clientOperate', // 客户新增/删除
	'/auth/getClientSelectLs': '/client/getClientSelectLs', // 客户下拉框
	'/auth/getClientLs': '/client/getClientLs', // 客户列表
	'/auth/clientOperateDelete': '/client/clientOperate', // 客户删除
	'/auth/addOrderOperate': '/orders/orderOperate', // 订单新增
	'/auth/orderOperate': '/orders/orderOperate', // 订单列表
	'/auth/rationOperate': '/orders/rationOperate', // 定量列表
	'/auth/AddrationOperate': '/orders/rationOperate', // 定量新增
	'/auth/DeleterationOperate': '/orders/rationOperate', // 定量删除
	'/auth/changePassword': '/manage_account/changePassword', // 用户更改密码
	'/auth/logout': '/manage_account/logout', // 退出登录
	'/auth/imageManage': '/product/imageManage', // 上传图片
	'/auth/getCommonDataForm': '/orders/getCommonDataForm', // 获取公共参数接口
});
// 获取公共参数接口
export function getCommonDataForm(data) {
	return doGet(API.dget('/auth/getCommonDataForm'), data);
}
// 上传图片
export function imageManage(data) {
	return doPostJson(API.dget('/auth/imageManage'), data);
}
// 退出登录
export function logout(data) {
	return doGet(API.dget('/auth/logout'), data);
}
// 用户更改密码
export function changePassword(data) {
	return doPUT(API.dget('/auth/changePassword'), data);
}
// 定量删除
export function DeleterationOperate(data) {
	return doDELETE(API.dget('/auth/DeleterationOperate'), data);
}
// 定量新增
export function AddrationOperate(data) {
	return doPostJson(API.dget('/auth/AddrationOperate'), data);
}
// 定量列表
export function rationOperate(data) {
	return doGet(API.dget('/auth/rationOperate'), data);
}
// 订单列表
export function orderOperate(data) {
	return doGet(API.dget('/auth/orderOperate'), data);
}
// 客户删除
export function addOrderOperate(data) {
	return doPostJson(API.dget('/auth/addOrderOperate'), data);
}
// 客户删除
export function clientOperateDelete(data) {
	return doDELETE(API.dget('/auth/clientOperateDelete'), data);
}
// 客户列表
export function getClientLs(data) {
	return doGet(API.dget('/auth/getClientLs'), data);
}
// 客户下拉框
export function getClientSelectLs(data) {
	return doGet(API.dget('/auth/getClientSelectLs'), data);
}
// 客户新增/删除
export function clientOperate(data) {
	return doPostJson(API.dget('/auth/clientOperate'), data);
}
// 用户登录
export function doLogin(data) {
	return doPostJson(API.dget('/auth/Login'), data);
}
// 用户信息
export function userinfo(data) {
	return doPostJson(API.dget('/auth/userinfo'), data);
}
// 商品分类
export function GoodsList(data) {
	return doGet(API.dget('/auth/GoodsList'), data);
}
// 加入购物车
export function shopCartUpdate(data) {
	return doPostJson(API.dget('/auth/shopCartUpdate'), data);
}
// 购物车列表
export function shopCartList(data) {
	return doGet(API.dget('/auth/shopCartList'), data);
}
// 购物车删除
export function shopCartUpdates(data) {
	return doDELETE(API.dget('/auth/shopCartUpdates'), data);
}
// 购物车数量
export function shopCartUpdateNum(data) {
	return doPUT(API.dget('/auth/shopCartUpdateNum'), data);
}
// 购物车数量
export function getPositionLs(data) {
	return doGet(API.dget('/auth/getPositionLs'), data);
}