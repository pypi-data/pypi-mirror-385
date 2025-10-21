# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import (
    div, div_accessibility, div_action, div_alignment_horizontal,
    div_alignment_vertical, div_animator, div_appearance_transition,
    div_background, div_border, div_change_transition,
    div_collection_item_builder, div_disappear_action, div_edge_insets,
    div_extension, div_focus, div_function, div_layout_provider, div_size,
    div_tooltip, div_transform, div_transformation, div_transition_trigger,
    div_trigger, div_variable, div_visibility, div_visibility_action,
)


# Gallery. It contains a horizontal or vertical set of cards that can be scrolled.
class DivGallery(BaseDiv):

    def __init__(
        self, *,
        type: str = "gallery",
        accessibility: typing.Optional[div_accessibility.DivAccessibility] = None,
        alignment_horizontal: typing.Optional[typing.Union[Expr, div_alignment_horizontal.DivAlignmentHorizontal]] = None,
        alignment_vertical: typing.Optional[typing.Union[Expr, div_alignment_vertical.DivAlignmentVertical]] = None,
        alpha: typing.Optional[typing.Union[Expr, float]] = None,
        animators: typing.Optional[typing.Sequence[div_animator.DivAnimator]] = None,
        background: typing.Optional[typing.Sequence[div_background.DivBackground]] = None,
        border: typing.Optional[div_border.DivBorder] = None,
        column_count: typing.Optional[typing.Union[Expr, int]] = None,
        column_span: typing.Optional[typing.Union[Expr, int]] = None,
        cross_content_alignment: typing.Optional[typing.Union[Expr, DivGalleryCrossContentAlignment]] = None,
        cross_spacing: typing.Optional[typing.Union[Expr, int]] = None,
        default_item: typing.Optional[typing.Union[Expr, int]] = None,
        disappear_actions: typing.Optional[typing.Sequence[div_disappear_action.DivDisappearAction]] = None,
        extensions: typing.Optional[typing.Sequence[div_extension.DivExtension]] = None,
        focus: typing.Optional[div_focus.DivFocus] = None,
        functions: typing.Optional[typing.Sequence[div_function.DivFunction]] = None,
        height: typing.Optional[div_size.DivSize] = None,
        id: typing.Optional[typing.Union[Expr, str]] = None,
        item_builder: typing.Optional[div_collection_item_builder.DivCollectionItemBuilder] = None,
        item_spacing: typing.Optional[typing.Union[Expr, int]] = None,
        items: typing.Optional[typing.Sequence[div.Div]] = None,
        layout_provider: typing.Optional[div_layout_provider.DivLayoutProvider] = None,
        margins: typing.Optional[div_edge_insets.DivEdgeInsets] = None,
        orientation: typing.Optional[typing.Union[Expr, DivGalleryOrientation]] = None,
        paddings: typing.Optional[div_edge_insets.DivEdgeInsets] = None,
        restrict_parent_scroll: typing.Optional[typing.Union[Expr, bool]] = None,
        reuse_id: typing.Optional[typing.Union[Expr, str]] = None,
        row_span: typing.Optional[typing.Union[Expr, int]] = None,
        scroll_mode: typing.Optional[typing.Union[Expr, DivGalleryScrollMode]] = None,
        scrollbar: typing.Optional[typing.Union[Expr, DivGalleryScrollbar]] = None,
        selected_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        tooltips: typing.Optional[typing.Sequence[div_tooltip.DivTooltip]] = None,
        transform: typing.Optional[div_transform.DivTransform] = None,
        transformations: typing.Optional[typing.Sequence[div_transformation.DivTransformation]] = None,
        transition_change: typing.Optional[div_change_transition.DivChangeTransition] = None,
        transition_in: typing.Optional[div_appearance_transition.DivAppearanceTransition] = None,
        transition_out: typing.Optional[div_appearance_transition.DivAppearanceTransition] = None,
        transition_triggers: typing.Optional[typing.Sequence[typing.Union[Expr, div_transition_trigger.DivTransitionTrigger]]] = None,
        variable_triggers: typing.Optional[typing.Sequence[div_trigger.DivTrigger]] = None,
        variables: typing.Optional[typing.Sequence[div_variable.DivVariable]] = None,
        visibility: typing.Optional[typing.Union[Expr, div_visibility.DivVisibility]] = None,
        visibility_action: typing.Optional[div_visibility_action.DivVisibilityAction] = None,
        visibility_actions: typing.Optional[typing.Sequence[div_visibility_action.DivVisibilityAction]] = None,
        width: typing.Optional[div_size.DivSize] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            accessibility=accessibility,
            alignment_horizontal=alignment_horizontal,
            alignment_vertical=alignment_vertical,
            alpha=alpha,
            animators=animators,
            background=background,
            border=border,
            column_count=column_count,
            column_span=column_span,
            cross_content_alignment=cross_content_alignment,
            cross_spacing=cross_spacing,
            default_item=default_item,
            disappear_actions=disappear_actions,
            extensions=extensions,
            focus=focus,
            functions=functions,
            height=height,
            id=id,
            item_builder=item_builder,
            item_spacing=item_spacing,
            items=items,
            layout_provider=layout_provider,
            margins=margins,
            orientation=orientation,
            paddings=paddings,
            restrict_parent_scroll=restrict_parent_scroll,
            reuse_id=reuse_id,
            row_span=row_span,
            scroll_mode=scroll_mode,
            scrollbar=scrollbar,
            selected_actions=selected_actions,
            tooltips=tooltips,
            transform=transform,
            transformations=transformations,
            transition_change=transition_change,
            transition_in=transition_in,
            transition_out=transition_out,
            transition_triggers=transition_triggers,
            variable_triggers=variable_triggers,
            variables=variables,
            visibility=visibility,
            visibility_action=visibility_action,
            visibility_actions=visibility_actions,
            width=width,
            **kwargs,
        )

    type: str = Field(default="gallery")
    accessibility: typing.Optional[div_accessibility.DivAccessibility] = Field(
        description="Accessibility settings.",
    )
    alignment_horizontal: typing.Optional[typing.Union[Expr, div_alignment_horizontal.DivAlignmentHorizontal]] = Field(
        description=(
            "Horizontal alignment of an element inside the parent "
            "element."
        ),
    )
    alignment_vertical: typing.Optional[typing.Union[Expr, div_alignment_vertical.DivAlignmentVertical]] = Field(
        description=(
            "Vertical alignment of an element inside the parent element."
        ),
    )
    alpha: typing.Optional[typing.Union[Expr, float]] = Field(
        description=(
            "Sets transparency of the entire element: `0` — completely "
            "transparent, `1` —opaque."
        ),
    )
    animators: typing.Optional[typing.Sequence[div_animator.DivAnimator]] = Field(
        description=(
            "Declaration of animators that change variable values over "
            "time."
        ),
    )
    background: typing.Optional[typing.Sequence[div_background.DivBackground]] = Field(
        description="Element background. It can contain multiple layers.",
    )
    border: typing.Optional[div_border.DivBorder] = Field(
        description="Element stroke.",
    )
    column_count: typing.Optional[typing.Union[Expr, int]] = Field(
        description="Number of columns for block layout.",
    )
    column_span: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Merges cells in a column of the [grid](div-grid.md) "
            "element."
        ),
    )
    cross_content_alignment: typing.Optional[typing.Union[Expr, DivGalleryCrossContentAlignment]] = Field(
        description=(
            "Aligning elements in the direction perpendicular to the "
            "scroll direction. Inhorizontal galleries:`start` — "
            "alignment to the top of the card;`center` — to "
            "thecenter;`end` — to the bottom.</p><p>In vertical "
            "galleries:`start` — alignment tothe left of the "
            "card;`center` — to the center;`end` — to the right."
        ),
    )
    cross_spacing: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Spacing between elements across the scroll axis. By "
            "default, the value set to`item_spacing`."
        ),
    )
    default_item: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Ordinal number of the gallery element to be scrolled to by "
            "default. For`scroll_mode`:`default` — the scroll position "
            "is set to the beginning of theelement, without taking into "
            "account `item_spacing`;`paging` — the scrollposition is set "
            "to the center of the element."
        ),
    )
    disappear_actions: typing.Optional[typing.Sequence[div_disappear_action.DivDisappearAction]] = Field(
        description="Actions when an element disappears from the screen.",
    )
    extensions: typing.Optional[typing.Sequence[div_extension.DivExtension]] = Field(
        description=(
            "Extensions for additional processing of an element. The "
            "list of extensions isgiven in "
            "[DivExtension](../../extensions)."
        ),
    )
    focus: typing.Optional[div_focus.DivFocus] = Field(
        description="Parameters when focusing on an element or losing focus.",
    )
    functions: typing.Optional[typing.Sequence[div_function.DivFunction]] = Field(
        description="User functions.",
    )
    height: typing.Optional[div_size.DivSize] = Field(
        description=(
            "Element height. For Android: if there is text in this or in "
            "a child element,specify height in `sp` to scale the element "
            "together with the text. To learn moreabout units of size "
            "measurement, see [Layout inside the card](../../layout)."
        ),
    )
    id: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "Element ID. It must be unique within the root element. It "
            "is used as`accessibilityIdentifier` on iOS."
        ),
    )
    item_builder: typing.Optional[div_collection_item_builder.DivCollectionItemBuilder] = Field(
        description=(
            "Sets collection elements dynamically using `data` and "
            "`prototypes`."
        ),
    )
    item_spacing: typing.Optional[typing.Union[Expr, int]] = Field(
        description="Spacing between elements.",
    )
    items: typing.Optional[typing.Sequence[div.Div]] = Field(
        description=(
            "Gallery elements. Scrolling to elements can be "
            "implementedusing:`div-action://set_current_item?id=&item=` "
            "— scrolling to the element withan ordinal number `item` "
            "inside an element, with the "
            "specified`id`;`div-action://set_next_item?id=[&overflow={cl"
            "amp\|ring}]` — scrolling to thenext element inside an "
            "element, with the "
            "specified`id`;`div-action://set_previous_item?id=[&overflow"
            "={clamp\|ring}]` — scrolling tothe previous element inside "
            "an element, with the specified `id`.</p><p>Theoptional "
            "`overflow` parameter is used to set navigation when the "
            "first or lastelement is reached:`clamp` — transition will "
            "stop at the border element;`ring` —go to the beginning or "
            "end, depending on the current element.</p><p>By "
            "default,`clamp`."
        ),
    )
    layout_provider: typing.Optional[div_layout_provider.DivLayoutProvider] = Field(
        description="Provides data on the actual size of the element.",
    )
    margins: typing.Optional[div_edge_insets.DivEdgeInsets] = Field(
        description="External margins from the element stroke.",
    )
    orientation: typing.Optional[typing.Union[Expr, DivGalleryOrientation]] = Field(
        description="Gallery orientation.",
    )
    paddings: typing.Optional[div_edge_insets.DivEdgeInsets] = Field(
        description="Internal margins from the element stroke.",
    )
    restrict_parent_scroll: typing.Optional[typing.Union[Expr, bool]] = Field(
        description=(
            "If the parameter is enabled, the gallery won\'t transmit "
            "the scroll gesture to theparent element."
        ),
    )
    reuse_id: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "ID for the div object structure. Used to optimize block "
            "reuse. See [blockreuse](../../reuse/reuse.md)."
        ),
    )
    row_span: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Merges cells in a string of the [grid](div-grid.md) "
            "element."
        ),
    )
    scroll_mode: typing.Optional[typing.Union[Expr, DivGalleryScrollMode]] = Field(
        description=(
            "Scroll type: `default` — continuous, `paging` — "
            "page-by-page."
        ),
    )
    scrollbar: typing.Optional[typing.Union[Expr, DivGalleryScrollbar]] = Field(
        description=(
            "Scrollbar behavior. Hidden by default. When choosing a "
            "gallery size, keep in mindthat the scrollbar may have a "
            "different height and width depending on theplatform and "
            "user settings. `none` — the scrollbar is hidden.`auto` — "
            "thescrollbar is shown if there isn\'t enough space and it "
            "needs to be displayed onthe current platform."
        ),
    )
    selected_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description=(
            "List of [actions](div-action.md) to be executed when "
            "selecting an element in[pager](div-pager.md)."
        ),
    )
    tooltips: typing.Optional[typing.Sequence[div_tooltip.DivTooltip]] = Field(
        description=(
            "Tooltips linked to an element. A tooltip can be shown "
            "by`div-action://show_tooltip?id=`, hidden by "
            "`div-action://hide_tooltip?id=` where`id` — tooltip id."
        ),
    )
    transform: typing.Optional[div_transform.DivTransform] = Field(
        description=(
            "Applies the passed transformation to the element. Content "
            "that doesn\'t fit intothe original view area is cut off."
        ),
    )
    transformations: typing.Optional[typing.Sequence[div_transformation.DivTransformation]] = Field(
        description=(
            "Array of transformations to be applied to the element in "
            "sequence."
        ),
    )
    transition_change: typing.Optional[div_change_transition.DivChangeTransition] = Field(
        description=(
            "Change animation. It is played when the position or size of "
            "an element changes inthe new layout."
        ),
    )
    transition_in: typing.Optional[div_appearance_transition.DivAppearanceTransition] = Field(
        description=(
            "Appearance animation. It is played when an element with a "
            "new ID appears. Tolearn more about the concept of "
            "transitions, see "
            "[Animatedtransitions](../../interaction#animation/transitio"
            "n-animation)."
        ),
    )
    transition_out: typing.Optional[div_appearance_transition.DivAppearanceTransition] = Field(
        description=(
            "Disappearance animation. It is played when an element "
            "disappears in the newlayout."
        ),
    )
    transition_triggers: typing.Optional[typing.Sequence[typing.Union[Expr, div_transition_trigger.DivTransitionTrigger]]] = Field(
        min_items=1, 
        description=(
            "Animation starting triggers. Default value: `[state_change, "
            "visibility_change]`."
        ),
    )
    variable_triggers: typing.Optional[typing.Sequence[div_trigger.DivTrigger]] = Field(
        description="Triggers for changing variables within an element.",
    )
    variables: typing.Optional[typing.Sequence[div_variable.DivVariable]] = Field(
        description=(
            "Declaration of variables that can be used within an "
            "element. Variables declaredin this array can only be used "
            "within the element and its child elements."
        ),
    )
    visibility: typing.Optional[typing.Union[Expr, div_visibility.DivVisibility]] = Field(
        description="Element visibility.",
    )
    visibility_action: typing.Optional[div_visibility_action.DivVisibilityAction] = Field(
        description=(
            "Tracking visibility of a single element. Not used if the "
            "`visibility_actions`parameter is set."
        ),
    )
    visibility_actions: typing.Optional[typing.Sequence[div_visibility_action.DivVisibilityAction]] = Field(
        description="Actions when an element appears on the screen.",
    )
    width: typing.Optional[div_size.DivSize] = Field(
        description="Element width.",
    )


class DivGalleryCrossContentAlignment(str, enum.Enum):
    START = "start"
    CENTER = "center"
    END = "end"


class DivGalleryOrientation(str, enum.Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class DivGalleryScrollMode(str, enum.Enum):
    PAGING = "paging"
    DEFAULT = "default"


class DivGalleryScrollbar(str, enum.Enum):
    NONE = "none"
    AUTO = "auto"


DivGallery.update_forward_refs()
