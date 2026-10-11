"""
Форматирование: цены и список товаров заказа.
"""
import html


def fmt_money(x: float) -> str:
    return f"{x:,.0f}$".replace(",", " ") if x == int(x) else f"{x:.2f}$"


def items_text(items: list[dict]) -> str:
    return "\n".join(
        f'• {html.escape(i["title"])}' + (f' [{html.escape(i["article"])}]' if i.get("article") else "")
        + f' — {i["qty"]} × {fmt_money(i["price"])}'
        for i in items)
