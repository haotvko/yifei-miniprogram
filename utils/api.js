// 云函数统一调用封装
function callFunction(name, data) {
  return new Promise((resolve, reject) => {
    wx.cloud.callFunction({
      name: name,
      data: data || {}
    }).then(res => {
      if (res && res.result) {
        resolve(res.result);
      } else {
        reject(new Error('云函数返回为空'));
      }
    }).catch(err => {
      reject(err);
    });
  });
}

module.exports = { callFunction };
