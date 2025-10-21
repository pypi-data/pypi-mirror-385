class Instrument:
    def __init__(self, instrument_id, exchange_id, instrument_name, product_id,
       product_type, create_date, open_date, expire_date,
       basis_price, volume_multiple, underlying_instrument_id,
       underlying_multiple, option_type, strike_price, price_tick,
       limit_price_min_vol):
        self.instrument_id = instrument_id
        self.exchange_id = exchange_id
        self.instrument_name = instrument_name
        self.product_id = product_id
        self.product_type = product_type
        self.create_date = create_date
        self.open_date = open_date
        self.expire_date = expire_date
        self.basis_price = basis_price
        self.volume_multiple = volume_multiple
        self.underlying_instrument_id = underlying_instrument_id
        self.underlying_multiple = underlying_multiple
        self.option_type = option_type
        self.strike_price = strike_price
        self.price_tick = price_tick
        self.limit_price_min_vol = limit_price_min_vol

    def __repr__(self):
        return (
            f"Instrument(instrument_id={self.instrument_id}, exchange_id={self.exchange_id}, "
            f"instrument_name={self.instrument_name}, product_id={self.product_id}, "
            f"product_type={self.product_type}, create_date={self.create_date}, "
            f"open_date={self.open_date}, expire_date={self.expire_date}, "
            f"basis_price={self.basis_price}, volume_multiple={self.volume_multiple}, "
            f"underlying_instrument_id={self.underlying_instrument_id}, underlying_multiple={self.underlying_multiple}, "
            f"option_type={self.option_type}, strike_price={self.strike_price}, "
            f"price_tick={self.price_tick}, limit_price_min_vol={self.limit_price_min_vol})"
        )
