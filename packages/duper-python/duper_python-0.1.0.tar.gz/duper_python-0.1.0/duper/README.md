# Duper

The format that's super.

Duper aims to be a human-friendly extension of JSON with quality-of-life improvements, extra types, and semantic identifiers.

## A visual introduction in four parts

For example, let's assume the following format for some product data in a storefront.

```duper
{
  "product_id": "1dd7b7aa-515e-405f-85a9-8ac812242609",
  "name": "Wireless Bluetooth Headphones",
  "brand": "AudioTech",
  "price": "129.99",
  "dimensions": [18.5, 15.2, 7.8],
  "weight": 0.285,
  "in_stock": true,
  "specifications": {
    "battery_life": "30h",
    "noise_cancellation": true,
    "connectivity": ["Bluetooth 5.0", "3.5mm Jack"]
  },
  "image_thumbnail": [137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 13, 73, 72, 68, 82, 0, 0, 0, 100],
  "tags": ["electronics", "audio", "wireless"],
  "release_date": "2023-11-15",
  "warranty_period": null,
  "customer_ratings": {
    "latest_review": "Absolutely \"\"astounding\"\"!! 😎",
    "average": 4.5,
    "count": 127
  },
  "created_at": "2023-11-17T21:50:43+00:00"
}
```

Plain ol' JSON. This is a valid Duper object, as well.

---

```duper
{
  product_id: "1dd7b7aa-515e-405f-85a9-8ac812242609",
  name: "Wireless Bluetooth Headphones",
  brand: "AudioTech",
  price: "129.99",
  dimensions: [18.5, 15.2, 7.8],  // In centimeters
  weight: 0.285,
  in_stock: true,
  specifications: {
    battery_life: "30h",
    noise_cancellation: true,
    connectivity: ["Bluetooth 5.0", "3.5mm Jack"],
  },
  image_thumbnail: [137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 13, 73, 72, 68, 82, 0, 0, 0, 100],
  tags: ["electronics", "audio", "wireless"],
  release_date: "2023-11-15",
  /* Warranty is optional */
  warranty_period: null,
  customer_ratings: {
    latest_review: "Absolutely \"\"astounding\"\"!! 😎",
    average: 4.5,
    count: 127,
  },
  created_at: "2023-11-17T21:50:43+00:00",
}
```

We can get rid of the quotes for simple keys, use trailing commas, and include comments. This is similar to [JSON5](https://json5.org/).

---

```duper
{
  product_id: "1dd7b7aa-515e-405f-85a9-8ac812242609",
  name: "Wireless Bluetooth Headphones",
  brand: "AudioTech",
  price: "129.99",
  dimensions: (18.5, 15.2, 7.8),  // In centimeters
  weight: 0.285,
  in_stock: true,
  specifications: {
    battery_life: "30h",
    noise_cancellation: true,
    connectivity: ["Bluetooth 5.0", "3.5mm Jack"],
  },
  image_thumbnail: b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x64",
  tags: ["electronics", "audio", "wireless"],
  release_date: "2023-11-15",
  /* Warranty is optional */
  warranty_period: null,
  customer_ratings: {
    latest_review: r#"Absolutely ""astounding""!! 😎"#,
    average: 4.5,
    count: 127,
  },
  created_at: "2023-11-17T21:50:43+00:00",
}
```

Duper also adds supports for tuples (`(-23.561384, -46.655891)`), bytes (`b"\x1b[1mDuper\x1b[0m"`), raw strings (`r#"I can use "quotes" in here!"#`), and raw bytes (`br"/\ Check this out! #wombo_combo"`). Also, integers are a separate type from floats.

---

```duper
Product({
  product_id: Uuid("1dd7b7aa-515e-405f-85a9-8ac812242609"),
  name: "Wireless Bluetooth Headphones",
  brand: "AudioTech",
  price: Decimal("129.99"),
  dimensions: (18.5, 15.2, 7.8),  // In centimeters
  weight: Kilograms(0.285),
  in_stock: true,
  specifications: {
    battery_life: Duration("30h"),
    noise_cancellation: true,
    connectivity: ["Bluetooth 5.0", "3.5mm Jack"],
  },
  image_thumbnail: Png(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x64"),
  tags: ["electronics", "audio", "wireless"],
  release_date: Date("2023-11-15"),
  /* Warranty is optional */
  warranty_period: null,
  customer_ratings: {
    latest_review: r#"Absolutely ""astounding""!! 😎"#,
    average: 4.5,
    count: 127,
  },
  created_at: DateTime("2023-11-17T21:50:43+00:00"),
})
```

Finally, Duper has the notion of _identifiers_: optional type-like annotations (`MyIdentifier(...)`) to help with readability, or to suggest that the parser handles/validates the data in a specific manner.
