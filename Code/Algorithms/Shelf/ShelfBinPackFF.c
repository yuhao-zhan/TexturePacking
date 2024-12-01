#include <stdio.h>
#include <stdlib.h>

#define MAX_ITEMS 100    // 最大物品数量
#define MAX_SHELVES 10   // 最大货架数量
#define WIDTH 100        // 货架的固定宽度

// 物品结构体
typedef struct {
    int width;   // 物品宽度
    int height;  // 物品高度
} Item;

// 货架结构体
typedef struct {
    int width;   // 当前货架的宽度，初始化为0
    int maxHeight; // 当前货架的最大物品高度
} Shelf;

// 全局变量：物品和货架
Item items[MAX_ITEMS];
Shelf shelves[MAX_SHELVES];

// 排序物品（按高度降序排列）
int compareItems(const void* a, const void* b) {
    Item* itemA = (Item*)a;
    Item* itemB = (Item*)b;
    return itemB->height - itemA->height; // 高度降序排序
}

// 将物品放入货架
void placeItemsOnShelves(Item items[], int numItems) {
    int numShelves = 0;  // 当前使用的货架数

    // 初始化货架
    for (int i = 0; i < MAX_SHELVES; i++) {
        shelves[i].width = 0;  // 每个货架从最左边开始
        shelves[i].maxHeight = 0; // 初始最大高度为 0
    }

    for (int i = 0; i < numItems; i++) {
        // 检查当前货架是否有足够的宽度来放置物品
        int placed = 0;  // 标记物品是否已放置
        for (int j = 0; j < numShelves; j++) {
            if (shelves[j].width + items[i].width <= WIDTH) {
                // 如果可以放下，放置物品并更新货架状态
                shelves[j].width += items[i].width;
                if (items[i].height > shelves[j].maxHeight) {
                    shelves[j].maxHeight = items[i].height;
                }
                placed = 1;
                break;
            }
        }

        // 如果物品没有放置在现有货架上，使用新的货架
        if (!placed && numShelves < MAX_SHELVES) {
            shelves[numShelves].width = items[i].width;
            shelves[numShelves].maxHeight = items[i].height;
            numShelves++;
        }
    }

    // 计算所有用到的货架的总高度
    int totalHeight = 0;
    for (int i = 0; i < numShelves; i++) {
        totalHeight += shelves[i].maxHeight;
    }

    // 输出每个货架的宽度和高度
    for (int i = 0; i < numShelves; i++) {
        printf("Shelf %d: Width %d, Height %d\n", i + 1, shelves[i].width, shelves[i].maxHeight);
    }

    // 输出总高度
    printf("Height of all shelves: %d\n", totalHeight);
}

int main() {
    int numItems;

    // 输入物品数量
    printf("The number of items: ");
    scanf("%d", &numItems);
    
    // 校验物品数量
    if (numItems < 1 || numItems > MAX_ITEMS) {
        printf("Warning: Amount of items out of range!\n");
        return -1;
    }

    // 输入每个物品的宽度和高度
    for (int i = 0; i < numItems; i++) {
        printf("Please input item %d's width and height: ", i + 1);
        scanf("%d %d", &items[i].width, &items[i].height);

        // 校验物品的宽度和高度
        if (items[i].width <= 0 || items[i].height <= 0) {
            printf("The width and height of item %d should be positive integers!\n", i + 1);
            return -1;
        }
    }
    
    printf("WIDTH = %d\n", WIDTH);
    // 按高度降序排序物品
    qsort(items, numItems, sizeof(Item), compareItems);

    // 放置物品到货架
    placeItemsOnShelves(items, numItems);

    return 0;
}
