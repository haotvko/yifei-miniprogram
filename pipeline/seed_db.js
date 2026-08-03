#!/usr/bin/env node
/**
 * 用已登录的 CloudBase CLI 把看板数据灌入云端：
 *   1) 建 snapshot 集合并写入 current 文档（伊菲当前掌握度 + 任务池）
 *   2) 建 uploads 集合（作业上传记录，先放一个占位文档确保集合存在）
 *
 * 用法：node pipeline/seed_db.js
 * 依赖：tcb CLI 已登录（tcb login），且 cloudbaserc.json 的 envId 正确。
 */
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const TCB = 'C:/Users/admin/.workbuddy/binaries/node/workspace/node_modules/@cloudbase/cli/bin/tcb';
const ENV = 'cloud1-d6gvwf6q09e5e6577';

function tcbDb(commandObj) {
  const cmd = JSON.stringify([commandObj]);
  return execFileSync('node', [TCB, 'db', 'nosql', 'execute', '-c', cmd, '-e', ENV], {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  });
}

function createColl(name) {
  try {
    tcbDb({ TableName: name, CommandType: 'CREATE', Command: JSON.stringify({ create: name }) });
    console.log(`✓ 集合 ${name} 已创建`);
  } catch (e) {
    const msg = (e.stderr || e.stdout || e.message || '').split('\n')[0];
    console.log(`· 集合 ${name} CREATE 跳过（可能已存在）：${msg.slice(0, 80)}`);
  }
}

function insertDoc(name, doc) {
  tcbDb({
    TableName: name,
    CommandType: 'INSERT',
    Command: JSON.stringify({ insert: name, documents: [doc] }),
  });
  console.log(`✓ 已写入 ${name} 文档（_id=${doc._id}）`);
}

const snapPath = path.join(__dirname, 'snapshot.json');
if (!fs.existsSync(snapPath)) {
  console.error('✗ 找不到 pipeline/snapshot.json，请先运行 export_snapshot.py');
  process.exit(1);
}
const snap = JSON.parse(fs.readFileSync(snapPath, 'utf8'));

// 1) snapshot 集合 + current 文档
createColl('snapshot');
const snapDoc = Object.assign({ _id: 'current' }, snap);
insertDoc('snapshot', snapDoc);

// 2) uploads 集合（占位文档，确保集合存在；真实上传由小程序写）
createColl('uploads');
insertDoc('uploads', { _id: '_init', note: 'init', created_at: new Date().toISOString() });

console.log('\n完成：云端 snapshot/uploads 已就绪。');
