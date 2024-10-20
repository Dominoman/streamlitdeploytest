from datetime import datetime, date
from typing import Optional, List, Dict, Tuple

from sqlalchemy import create_engine, TIMESTAMP, ForeignKey, String, Table, Column, and_, select, delete, exists, not_, \
    Index, ForeignKeyConstraint, BOOLEAN, Update
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column, relationship, Query, aliased


class Base(DeclarativeBase):
    def compare(self, new_route: 'Base') -> Dict[str, Tuple[str, str]]:
        return {
            item: (
                str(self.__getattribute__(item)),
                str(new_route.__getattribute__(item)),
            )
            for item in self.__dict__
            if item != "_sa_instance_state"
               and self.__getattribute__(item) != new_route.__getattribute__(item)
        }


class Search(Base):
    __tablename__ = "search"

    search_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    url: Mapped[str] = mapped_column(String(2048))
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
    range_start: Mapped[date]
    range_end: Mapped[date]
    results: Mapped[int]
    actual: Mapped[bool] = mapped_column(BOOLEAN, default=False, index=True)

    itineraries: Mapped[List["Itinerary"]] = relationship(back_populates="parent")

    def __repr__(self):
        return (
            f"<Search(search_id={self.search_id!r}, url={self.url!r}, "
            f"timestamp={self.timestamp!r}, range_start={self.range_start!r}, "
            f"range_end={self.range_end!r}, results={self.results!r})>"
        )


itinerary2route_table = Table("itinerary2route", Base.metadata,
                              Column("search_id",String(36), primary_key=True),
                              Column("itinerary_id",String(255), primary_key=True),
                              Column("route_id",String(26), ForeignKey("route.id"), primary_key=True),
                              Index('route_idx','route_id'),
                              ForeignKeyConstraint(
                                  ['search_id','itinerary_id'],
                                  ['itinerary.search_id','itinerary.id']
                              )
                              )


class Itinerary(Base):
    __tablename__ = "itinerary"

    search_id: Mapped[str] = mapped_column(String(36), ForeignKey("search.search_id"), primary_key=True)
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    flyFrom: Mapped[str] = mapped_column(String(3))
    flyTo: Mapped[str] = mapped_column(String(3))
    cityFrom: Mapped[str] = mapped_column(String(50))
    cityCodeFrom: Mapped[str] = mapped_column(String(3))
    cityTo: Mapped[str] = mapped_column(String(50))
    cityCodeTo: Mapped[str] = mapped_column(String(3))
    countryFromCode: Mapped[str] = mapped_column(String(2))
    countryFromName: Mapped[str] = mapped_column(String(50))
    countryToCode: Mapped[str] = mapped_column(String(2))
    countryToName: Mapped[str] = mapped_column(String(50))
    local_departure: Mapped[datetime]
    local_arrival: Mapped[datetime]
    nightsInDest: Mapped[int]
    quality: Mapped[float]
    distance: Mapped[float]
    durationDeparture: Mapped[int]
    durationReturn: Mapped[int]
    price: Mapped[float]=mapped_column(index=True)
    conversionEUR: Mapped[float]
    availabilitySeats: Mapped[Optional[int]]
    airlines: Mapped[str] = mapped_column(String(30))
    booking_token: Mapped[str] = mapped_column(String(2048))
    deep_link: Mapped[str] = mapped_column(String(2048))
    facilitated_booking_available: Mapped[bool]
    pnr_count: Mapped[int]
    has_airport_change: Mapped[bool]
    technical_stops: Mapped[int]
    throw_away_ticketing: Mapped[bool]
    hidden_city_ticketing: Mapped[bool]
    virtual_interlining: Mapped[bool]

    parent: Mapped["Search"] = relationship(back_populates="itineraries")
    routes: Mapped[List['Route']] = relationship(secondary=itinerary2route_table,
                                                 primaryjoin=lambda: and_(
                                                     itinerary2route_table.c.search_id == Itinerary.search_id,
                                                     itinerary2route_table.c.itinerary_id == Itinerary.id),
                                                 secondaryjoin=lambda: itinerary2route_table.c.route_id == Route.id,
                                                 back_populates="itineraries")

    def __repr__(self):
        return (
            f"<Itinerary(search_id={self.search_id!r}, id={self.id!r}, "
            f"flyFrom={self.flyFrom!r}, flyTo={self.flyTo!r}, "
            f"local_departure={self.local_departure!r}, local_arrival={self.local_arrival!r}, "
            f"nightsInDest={self.nightsInDest!r}, price={self.price!r}, "
            f"quality={self.quality!r}, distance={self.distance!r})>"
        )


class Route(Base):
    __tablename__ = "route"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    combination_id: Mapped[str] = mapped_column(String(24))
    flyFrom: Mapped[str] = mapped_column(String(3))
    flyTo: Mapped[str] = mapped_column(String(3))
    cityFrom: Mapped[str] = mapped_column(String(50))
    cityCodeFrom: Mapped[str] = mapped_column(String(3))
    cityTo: Mapped[str] = mapped_column(String(50))
    cityCodeTo: Mapped[str] = mapped_column(String(3))
    local_departure: Mapped[datetime]
    local_arrival: Mapped[datetime]
    airline: Mapped[str] = mapped_column(String(2))
    flight_no: Mapped[int]
    operating_carrier: Mapped[str] = mapped_column(String(2))
    operating_flight_no: Mapped[str] = mapped_column(String(4))
    fare_basis: Mapped[str] = mapped_column(String(10))
    fare_category: Mapped[str] = mapped_column(String(1))
    fare_classes: Mapped[str] = mapped_column(String(1))
    _return: Mapped[int]
    bags_recheck_required: Mapped[bool]
    vi_connection: Mapped[bool]
    guarantee: Mapped[bool]
    equipment: Mapped[Optional[str]] = mapped_column(String(4))
    vehicle_type: Mapped[str] = mapped_column(String(8))

    itineraries: Mapped[List[Itinerary]] = relationship(secondary=itinerary2route_table,
                                                        primaryjoin=lambda: itinerary2route_table.c.route_id == Route.id,
                                                        secondaryjoin=lambda: and_(
                                                            itinerary2route_table.c.search_id == Itinerary.search_id,
                                                            itinerary2route_table.c.itinerary_id == Itinerary.id),
                                                        back_populates="routes")

    def __repr__(self):
        return (
            f"<Route(id={self.id!r}, combination_id={self.combination_id!r}, "
            f"flyFrom={self.flyFrom!r}, flyTo={self.flyTo!r}, "
            f"local_departure={self.local_departure!r}, local_arrival={self.local_arrival!r}, "
            f"airline={self.airline!r}, flight_no={self.flight_no!r}, "
            f"vehicle_type={self.vehicle_type!r})>"
        )


class Database:
    def __init__(self, db_url: str, debug: bool = False) -> None:
        self.engine = create_engine(db_url, echo=debug)
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)

    def insert_json(self, json_data: dict, url: str = "", timestamp: datetime = None, range_start: date = None,
                    range_end: date = None,actual:bool=True) -> bool:
        old_search = self.session.query(Search).get(json_data["search_id"])
        if old_search is not None:
            return False
        if timestamp is None:
            timestamp = datetime.now()
        new_search = Search(search_id=json_data["search_id"], url=url, timestamp=timestamp,
                            results=json_data["_results"], range_start=range_start, range_end=range_end, actual=actual)
        self.session.add(new_search)
        for itinerary in json_data["data"]:
            local_departure = datetime.strptime(itinerary["local_departure"], "%Y-%m-%dT%H:%M:%S.000Z")
            local_arrival = datetime.strptime(itinerary["local_arrival"], "%Y-%m-%dT%H:%M:%S.000Z")
            airlines = ','.join(itinerary["airlines"])
            # booking_token és a deep_link túl sok helyet foglal, kihagyjuk
            new_itinerary = Itinerary(search_id=json_data["search_id"], id=itinerary["id"],
                                      flyFrom=itinerary["flyFrom"],
                                      flyTo=itinerary["flyTo"], cityFrom=itinerary["cityFrom"],
                                      cityCodeFrom=itinerary["cityCodeFrom"], cityTo=itinerary["cityTo"],
                                      cityCodeTo=itinerary["cityCodeTo"],
                                      countryFromCode=itinerary["countryFrom"]["code"],
                                      countryFromName=itinerary["countryFrom"]["name"],
                                      countryToCode=itinerary["countryTo"]["code"],
                                      countryToName=itinerary["countryTo"]["name"], local_departure=local_departure,
                                      local_arrival=local_arrival, nightsInDest=itinerary["nightsInDest"],
                                      quality=itinerary["quality"], distance=itinerary["distance"],
                                      durationDeparture=itinerary["duration"]["departure"],
                                      durationReturn=itinerary["duration"]["return"], price=itinerary["price"],
                                      conversionEUR=itinerary["conversion"]["EUR"],
                                      availabilitySeats=itinerary["availability"]["seats"], airlines=airlines,
                                      booking_token='', deep_link='',
                                      facilitated_booking_available=itinerary["facilitated_booking_available"],
                                      pnr_count=itinerary["pnr_count"],
                                      has_airport_change=itinerary["has_airport_change"],
                                      technical_stops=itinerary["technical_stops"],
                                      throw_away_ticketing=itinerary["throw_away_ticketing"],
                                      hidden_city_ticketing=itinerary["hidden_city_ticketing"],
                                      virtual_interlining=itinerary["virtual_interlining"])
            self.session.add(new_itinerary)
            for route in itinerary["route"]:
                self.add_route(new_itinerary, route)
            self.session.commit()
        return True

    def add_route(self, itinerary_obj: Itinerary, route: dict) -> bool:
        local_departure = datetime.strptime(route["local_departure"], "%Y-%m-%dT%H:%M:%S.000Z")
        local_arrival = datetime.strptime(route["local_arrival"], "%Y-%m-%dT%H:%M:%S.000Z")
        new_route = Route(id=route["id"], combination_id=route["combination_id"], flyFrom=route["flyFrom"],
                          flyTo=route["flyTo"], cityFrom=route["cityFrom"], cityCodeFrom=route["cityCodeFrom"],
                          cityTo=route["cityTo"], cityCodeTo=route["cityCodeTo"], local_departure=local_departure,
                          local_arrival=local_arrival, airline=route["airline"], flight_no=route["flight_no"],
                          operating_carrier=route["operating_carrier"],
                          operating_flight_no=route["operating_flight_no"],
                          fare_basis=route["fare_basis"], fare_category=route["fare_category"],
                          fare_classes=route["fare_classes"], _return=route["return"],
                          bags_recheck_required=route["bags_recheck_required"],
                          vi_connection=route["vi_connection"],
                          guarantee=route["guarantee"], equipment=route["equipment"],
                          vehicle_type=route["vehicle_type"])

        old_route = self.session.query(Route).get(route["id"])
        if old_route is None:
            itinerary_obj.routes.append(new_route)
            return True
        diff = old_route.compare(new_route)
        if len(diff) > 0:
            self.make_history(old_route, diff)
        itinerary_obj.routes.append(old_route)
        return False

    @staticmethod
    def make_history(old_route: Route, diff: Dict[str, Tuple[str, str]]) -> None:
        for k, v in diff.items():
            if k not in ["local_departure", "local_arrival"]:
                old_route.__setattr__(k, v[1])

    def get_all_search(self) -> Query:
        return self.session.query(Search)

    def delete_search(self, search: Search) -> None:
        search_id = search.search_id

        t1 = aliased(itinerary2route_table)
        t2 = aliased(itinerary2route_table)

        subquery = select(1).where(and_(t2.c.route_id==t1.c.route_id,t2.c.search_id!=search_id))
        mainquery=select(t1.c.route_id).where(and_(t1.c.search_id==search_id, not_(exists(subquery))))

        result = list(self.session.execute(mainquery).scalars())

        delete_i2r = delete(itinerary2route_table).where(itinerary2route_table.c.search_id == search_id)
        self.session.execute(delete_i2r)

        delete_route = delete(Route).where(Route.id.in_(result))
        self.session.execute(delete_route)

        delete_itinerary = delete(Itinerary).where(Itinerary.search_id == search_id)
        self.session.execute(delete_itinerary)

        self.session.delete(search)
        self.session.commit()

    def clean_actual_flag(self)->None:
        update=Update(Search).where(Base.metadata.tables["search"].c.actual==True).values(actual=False)
        self.session.execute(update)
        self.session.commit()