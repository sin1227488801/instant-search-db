// モックデータ - 実際のCSVデータから抜粋
const mockData = [
    // 武器
    { category: "武器", name: "つるはし", description: "攻 1 買 240 補正 12 売 100 補正 7テ ○掛 拾食 ×フェイ ○変 ○鍛 ×能力 壁を掘れるが、何度か掘ると壊れる" },
    { category: "武器", name: "必中の剣", description: "攻 2 買 10000 補正 900 売 5000 補正 475テ 店掛 ×食 ×フェイ ○変 ○鍛 ×能力 攻撃が必ず当たる" },
    { category: "武器", name: "妖刀かまいたち", description: "攻 3 買 5000 補正 380 売 2000 補正 170テ ○掛 ×食 ×フェイ ○変 ○鍛 ×能力 前方3方向に攻撃可" },
    { category: "武器", name: "成仏の鎌", description: "攻 4 買 2000 補正 150 売 900 補正 75テ ○掛 ×食 ×フェイ ○変 ○鍛 ×能力 ゴースト系に2倍ダメージ。ぼうれい武者の１ダメージ化を無効" },
    { category: "武器", name: "カタナ", description: "攻 6 買 800 補正 80 売 300 補正 30テ ○掛 ○食 ×フェイ ○変 ○鍛 ×能力 －" },
    { category: "武器", name: "ドラゴンキラー", description: "攻 7 買 3600 補正 310 売 1200 補正 107テ 店掛 ×食 ×フェイ ○変 ○鍛 ×能力 ドラゴン系に2倍ダメージ" },
    { category: "武器", name: "どうたぬき", description: "攻 8 買 1200 補正 120 売 400 補正 40テ ○掛 ○食 ×フェイ ○変 ○鍛 ×能力 －" },
    { category: "武器", name: "剛剣マンジカブラ", description: "攻 12 買 15000 補正 1500 売 7000 補正 700テ ○掛 ×食 ×フェイ ○変 ○鍛 ×能力 こばみ谷で変化の壺から希に入手" },

    // 盾
    { category: "盾", name: "皮甲の盾", description: "防 2 買 1000 補正 40 売 350 補正 20テ ○掛 －食 ○フェイ ○変 ○鍛 －能力 錆びない。満腹度の減りが1/2になる" },
    { category: "盾", name: "木甲の盾", description: "防 3 買 600 補正 40 売 200 補正 15テ ○掛 店食 ○フェイ ○変 ○鍛 －能力 錆びない" },
    { category: "盾", name: "青銅甲の盾", description: "防 4 買 300 補正 30 売 100 補正 10テ ○掛 ○食 ○フェイ ○変 ○鍛 －能力 －" },
    { category: "盾", name: "バトルカウンター", description: "防 5 買 5000 補正 250 売 2500 補正 125テ 店掛 ○食 ○フェイ ○変 ○鍛 －能力 受けたダメージの1/3を返す" },
    { category: "盾", name: "見切りの盾", description: "買 7500 補正 500 売 3000 補正 150テ 店掛 ○食 店フェイ ○変 ○鍛 －能力 攻撃を1/2の確率でかわす" },
    { category: "盾", name: "やまびこの盾", description: "買 12000 補正 600 売 6000 補正 300テ 店掛 －食 店フェイ ○変 ○鍛 －能力 魔法を跳ね返す" },
    { category: "盾", name: "風魔の盾", description: "防 12 買 5000 補正 500 売 2500 補正 250テ －掛 －食 －フェイ ○変 ○鍛 －能力 こばみ谷で変化の壺から希に入手" },

    // 矢
    { category: "矢", name: "木の矢", description: "買 10 売 2テ ○掛 ○食 ○フェイ ○備考 唯一普通に手に入る矢ボウヤーが撃ってくる" },
    { category: "矢", name: "鉄の矢", description: "買 40 売 10テ モ掛 モ食 モフェイ 店備考 攻撃力最高。店は16F以降クロスボウヤー、コドモ戦車が撃ってくる" },
    { category: "矢", name: "銀の矢", description: "買 80 売 20テ ×掛 ×食 ×フェイ 店備考 貫通能力がある。店は51F以降ちびタンクが撃ってくる" },

    // 腕輪
    { category: "腕輪", name: "遠投の腕輪", description: "買 1200 売 600テ ○掛 ×食 ×フェイ ○備考 自分の撃った矢やアイテムの投擲が射程無限・貫通になる" },
    { category: "腕輪", name: "呪いよけの腕輪", description: "買 2400 売 1200テ ○掛 ×食 ×フェイ ○備考 ノロージョ系の能力による呪いを防ぐ元々呪われている装備品の呪いは解けない" },
    { category: "腕輪", name: "透視の腕輪", description: "買 3600 売 1800テ ○掛 ×食 ×フェイ ○備考 マップ上の赤点(モンスターとNPC)・青点(アイテム)の位置が分かる" },
    { category: "腕輪", name: "回復の腕輪", description: "買 5000 売 2500テ 店掛 ×食 ×フェイ ○備考 1ターンにHPが5回復するが、満腹度の減り方が2倍になる" },
    { category: "腕輪", name: "しあわせの腕輪", description: "買 10000 売 5000テ 店掛 ×食 ×フェイ ○備考 1ターンに経験値が1増える。町の中では無効" },

    // 杖
    { category: "杖", name: "痛み分けの杖", description: "テ ○ 掛 × 食 × フェイ ○ モ × 備考 自分がダメージを受けた時、振ったモンスターにも同じダメージを与える" },
    { category: "杖", name: "一時しのぎの杖", description: "テ ○ 掛 × 食 × フェイ ○ モ × 備考 階段の上にワープさせ、金縛り状態にする" },
    { category: "杖", name: "かなしばりの杖", description: "テ ○ 掛 ○ 食 × フェイ ○ モ × 備考 金縛り状態にする" },
    { category: "杖", name: "しあわせの杖", description: "テ × 掛 × 食 店 フェイ ○ モ × 備考 レベルを1上げるプレイヤーに当たった場合は経験値+500" },
    { category: "杖", name: "場所替えの杖", description: "テ ○ 掛 ○ 食 店 フェイ ○ モ × 備考 振った相手と自分の位置が入れ替わる" },
    { category: "杖", name: "身がわりの杖", description: "テ ○ 掛 × 食 店 フェイ ○ モ × 備考 振った相手をにせプレイヤーにするモンスターはにせプレイヤーを攻撃するようになる" },

    // 壺
    { category: "壺", name: "やりすごしの壺", description: "テ ○ 掛 店 食 × フェイ ○ 備考 プレイヤーが入ると20ターン壺の中に隠れ、モンスターに見つからなくなる" },
    { category: "壺", name: "保存の壺", description: "テ ○ 掛 × 食 ○ フェイ ○ 備考 「見る」ことでアイテムを出し入れできる壺の中のアイテムを直接使用できる" },
    { category: "壺", name: "底抜けの壺", description: "テ × 掛 × 食 ○ フェイ ○ 備考 アイテムを入れると消滅する。割れるか吸い出すと落とし穴ができる" },
    { category: "壺", name: "識別の壺", description: "テ ○ 掛 × 食 × フェイ ○ 備考 入れたアイテムが識別される" },
    { category: "壺", name: "変化の壺", description: "テ ○ 掛 × 食 × フェイ ○ 備考 入れたアイテムが他のアイテムに変わる。同じアイテムになることもある" },
    { category: "壺", name: "合成の壺", description: "テ ○ 掛 × 食 × フェイ ○ 備考 武器･盾の修正値や能力、杖の回数をかけ合わせる" },

    // 巻物
    { category: "巻物", name: "モンスターハウスの巻物", description: "買 80 売 40 テ × 掛 ○ 食 × フェイ ○ 備考 フロア中のモンスターが消滅し、今いる部屋がモンスターハウスになる" },
    { category: "巻物", name: "混乱の巻物", description: "買 100 売 50 テ ○ 掛 × 食 × フェイ × 備考 同じ部屋(通路では周囲)のモンスター･NPCが混乱状態になる" },
    { category: "巻物", name: "バクスイの巻物", description: "買 200 売 100 テ ○ 掛 × 食 × フェイ × 備考 同じ部屋(通路では周囲)のモンスター･NPCを20ターン睡眠状態にする" },
    { category: "巻物", name: "識別の巻物", description: "買 300 売 150 テ ○ 掛 ○ 食 店 フェイ ○ 備考 アイテムを1つ識別できる。低確率で全て識別される" },
    { category: "巻物", name: "あかりの巻物", description: "買 300 売 250 テ ○ 掛 ○ 食 店 フェイ × 備考 フロアのマップ・モンスター・NPC・アイテムの位置が分かるようになる" },
    { category: "巻物", name: "大部屋の巻物", description: "買 400 売 200 テ ○ 掛 ○ 食 店 フェイ ○ 備考 フロアを大部屋にする。シャッフルダンジョンでは無効" },

    // 草・種
    { category: "草・種", name: "雑草", description: "買 50 売 25 テ モ 掛 モ 食 モ フェイ モ 効果・補足 畠荒らしの能力、復活の草の効果によって入手できる特殊効果のない草" },
    { category: "草・種", name: "めぐすり草", description: "買 50 売 25 テ ○ 掛 × 食 ○ フェイ ○ 効果・補足 罠やエーテルデビルが見えるようになる" },
    { category: "草・種", name: "薬草", description: "買 50 売 25 テ ○ 掛 ○ 食 ○ フェイ ○ 効果・補足 HPが25回復する。HPが最大の時に飲むとHPの最大値が1上昇" },
    { category: "草・種", name: "弟切草", description: "買 100 売 50 テ ○ 掛 ○ 食 ○ フェイ ○ 効果・補足 HPが100回復する。HPが最大の時に飲むとHPの最大値が2上昇" },
    { category: "草・種", name: "命の草", description: "買 500 売 200 テ ○ 掛 ○ 食 店 フェイ ○ 効果・補足 HPの最大値が5上がる" },
    { category: "草・種", name: "ちからの草", description: "買 500 売 250 テ 店 掛 店 食 店 フェイ ○ 効果・補足 ちからが全快の時に飲むとちからの最大値が1上がる" },
    { category: "草・種", name: "しあわせ草", description: "買 1000 売 500 テ × 掛 × 食 × フェイ ○ 効果・補足 レベルが1上がる" },
    { category: "草・種", name: "復活の草", description: "買 5000 売 2500 テ 店 掛 × 食 × フェイ ○ 効果・補足 持っていると死んだ時に一度だけ復活できる。復活後は雑草に変化する" },

    // にぎり
    { category: "にぎり", name: "おにぎり", description: "買 100 売 25 テ ○ 掛 ○ 食 × フェイ ○ 効果・補足 満腹度を50%回復。満腹なら最大満腹度+1%" },
    { category: "にぎり", name: "大きいおにぎり", description: "買 200 売 50 テ ○ 掛 ○ 食 × フェイ ○ 効果・補足 満腹度を100%回復。満腹なら+2%" },
    { category: "にぎり", name: "巨大なおにぎり", description: "買 300 売 75 テ ○ 掛 ○ 食 × フェイ ○ 効果・補足 満腹度を最大まで回復し、最大満腹度が5%上がる" },
    { category: "にぎり", name: "くさったおにぎり", description: "買 100 売 25 テ ○ 掛 罠 食 × フェイ ○ 効果・補足 満腹度を30%回復し、目つぶし、混乱、睡眠、ちから-3、レベルダウンのいずれかの効果" },

    // その他
    { category: "その他", name: "モンスターの肉", description: "（全120種）" }
];

// カテゴリ設定
const categories = {
    "武器": {
        "display_name": "武器",
        "icon": "fas fa-hammer",
        "emoji_fallback": "⚔️",
        "color": "#e74c3c",
        "description": "攻撃用の武器類"
    },
    "盾": {
        "display_name": "盾",
        "icon": "fas fa-shield-alt",
        "emoji_fallback": "🛡️",
        "color": "#3498db",
        "description": "防御用の盾類"
    },
    "矢": {
        "display_name": "矢",
        "icon": "fas fa-arrow-up",
        "emoji_fallback": "🏹",
        "color": "#f39c12",
        "description": "射撃用の矢類"
    },
    "腕輪": {
        "display_name": "腕輪",
        "icon": "fas fa-ring",
        "emoji_fallback": "💍",
        "color": "#9b59b6",
        "description": "特殊効果のある腕輪類"
    },
    "杖": {
        "display_name": "杖",
        "icon": "fas fa-magic",
        "emoji_fallback": "🪄",
        "color": "#8e44ad",
        "description": "魔法効果のある杖類"
    },
    "壺": {
        "display_name": "壺",
        "icon": "fas fa-flask",
        "emoji_fallback": "🏺",
        "color": "#16a085",
        "description": "アイテム保存や特殊効果のある壺類"
    },
    "巻物": {
        "display_name": "巻物",
        "icon": "fas fa-scroll",
        "emoji_fallback": "📜",
        "color": "#f1c40f",
        "description": "一度使用すると消える巻物類"
    },
    "草・種": {
        "display_name": "草・種",
        "icon": "fas fa-seedling",
        "emoji_fallback": "🌱",
        "color": "#27ae60",
        "description": "回復や特殊効果のある草・種類"
    },
    "にぎり": {
        "display_name": "にぎり",
        "icon": "fas fa-cookie-bite",
        "emoji_fallback": "🍙",
        "color": "#e67e22",
        "description": "満腹度を回復するおにぎり類"
    },
    "その他": {
        "display_name": "その他",
        "icon": "fas fa-question",
        "emoji_fallback": "❓",
        "color": "#95a5a6",
        "description": "その他のアイテム"
    }
};

// カテゴリ別アイテム数を計算
function getCategoryCounts() {
    const counts = {};
    Object.keys(categories).forEach(key => {
        counts[key] = mockData.filter(item => item.category === key).length;
    });
    return counts;
}