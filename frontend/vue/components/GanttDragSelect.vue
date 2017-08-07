<template>
    <div class="drag-select" ref="dragSelectContainer"
        @mousedown="handleMouseDown"
        @mousemove="handleMouseMove"
        @mouseup="handleMouseUp"
        >
        <slot></slot>
        <div ref="selectionAreaIndicator" class="selection-area-indicator" v-show="selecting"></div>
    </div>
</template>

<script>
export default {
    name: 'GanttDragSelect',
    props: ['item-selector', 'value', 'editing'],
    data() {
        return {
            selecting: false,
            startPoint: null,
        }
    },
    methods: {
        handleMouseDown(event) {
            if (!this.editing) {
                return false;
            }

            event.preventDefault();
            if (event.target.classList.contains('drag-select') || event.target.classList.contains('row-line')) {
                var $dragSelectContainer = $(this.$refs.dragSelectContainer);
                var twOffset = $dragSelectContainer.offset();
                var $selectionMarker = $(this.$refs.selectionAreaIndicator);
                var x = event.pageX - twOffset.left;
                var y = event.pageY - twOffset.top;

                $selectionMarker
                    .css({
                        left: x,
                        top: y,
                        width: 0,
                        height: 0,
                    })
                    .addClass('active');

                this.startPoint = { x, y };
                this.selecting = true;
            }
        },
        handleMouseMove(event) {
            if (!this.editing) {
                return false;
            }

            if (this.selecting) {
                event.preventDefault();

                var $dragSelectContainer = $(this.$refs.dragSelectContainer);
                var twOffset = $dragSelectContainer.offset();
                var $selectionMarker = $(this.$refs.selectionAreaIndicator);

                var ix = this.startPoint.x;
                var iy = this.startPoint.y;
                var x = event.pageX - twOffset.left;
                var y = event.pageY - twOffset.top;
                var w = Math.abs(ix - x);
                var h = Math.abs(iy - y);

                $selectionMarker.css({
                    width: w,
                    height: h,
                });
                if (x < ix) {
                    $selectionMarker.css('left', x);
                }
                if (y < iy) {
                    $selectionMarker.css('top', y);
                }
            }
        },
        handleMouseUp(event) {
            if (!this.editing) {
                return false;
            }

            if (this.selecting) {
                event.preventDefault();

                var $dragSelectContainer = $(this.$refs.dragSelectContainer);
                var $selectionMarker = $(this.$refs.selectionAreaIndicator);
                var sx = $selectionMarker.offset().left;
                var sy = $selectionMarker.offset().top;
                var sxe = sx + parseInt($selectionMarker.css('width').replace('px', ''));
                var sye = sy + parseInt($selectionMarker.css('height').replace('px', ''));
                var $bars = $dragSelectContainer.find(this.itemSelector + ':not(.assigned)');

                var selectedItems = this.value;

                if (!event.shiftKey && !event.altKey) {
                    selectedItems = {};
                }

                var self = this;
                $bars.each(function() {
                    var $bar = $(this);
                    var bx = $bar.offset().left;
                    var by = $bar.offset().top;
                    var bxe = bx + parseInt($bar.css('width').replace('px', ''));
                    var bye = by + parseInt($bar.css('height').replace('px', ''));

                    if (
                        ((bx >= sx && bx <= sxe) || (bxe >= sx && bxe <= sxe) || (bx <= sx && bxe >= sxe))
                        && ((by >= sy && by <= sye) || (bye >= sy && bye <= sye) || (by <= sy && bye >= sye))
                    ) {
                        var barData = $bar.closest('.gantt-bar')[0].__vue__.data;
                        if (event.altKey) {
                            if (selectedItems[barData.id]) {
                                self.$delete(selectedItems, barData.id);
                            }
                        } else {
                            self.$set(selectedItems, barData.id, barData);
                        }
                    }
                });

                this.$emit('input', selectedItems);
                this.selecting = false;
            }
        },
    },
}
</script>

<style type="text/css">
    .drag-select {
        position: relative;
    }
</style>