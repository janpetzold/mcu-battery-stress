
use std::{
    thread::sleep,
    time::Duration,
};

use embedded_svc::wifi::{AuthMethod, ClientConfiguration, Configuration};
use esp_idf_hal::peripherals::Peripherals;
use esp_idf_svc::eventloop::EspSystemEventLoop;
use esp_idf_svc::nvs::EspDefaultNvsPartition;
use esp_idf_svc::wifi::EspWifi;

// EMbedded String type handling
use heapless::String;
use std::str::FromStr;

use bme680::*;
use esp_idf_hal::delay::Delay;
use esp_idf_hal::i2c;
use esp_idf_hal::prelude::*;

fn main() {
    // It is necessary to call this function once. Otherwise some patches to the runtime
    // implemented by esp-idf-sys might not link properly. See https://github.com/esp-rs/esp-idf-template/issues/71
    esp_idf_svc::sys::link_patches();

    // Bind the log crate to the ESP Logging facilities
    esp_idf_svc::log::EspLogger::initialize_default();

    log::info!("Starting up");

    // Configure Peripherals
    let peripherals = Peripherals::take().unwrap();
    let sys_loop = EspSystemEventLoop::take().unwrap();
    let nvs = EspDefaultNvsPartition::take().unwrap();

    // Delayer
    let system_clock_hz: u32 = 40_000_000; // 40 MHz for Llolin32
    let mut delayer = Delay::new(system_clock_hz);

    /*
    // Setup I2C configuration
    let config = i2c::config::MasterConfig::new()
        .baudrate(400.kHz().into()) // Set baudrate
        .timeout_ms(1000); // Set timeout

    // Instantiate the I2C master
    let i2c = i2c::Master::<i2c::I2C0, _, _>::new(
        peripherals.i2c0, 
        pins.gpio21, // SDA pin
        pins.gpio22, // SCL pin
        config
    ).unwrap();
    */


    let settings = SettingsBuilder::new()
        .with_humidity_oversampling(OversamplingSetting::OS2x)
        .with_pressure_oversampling(OversamplingSetting::OS4x)
        .with_temperature_oversampling(OversamplingSetting::OS8x)
        .with_temperature_filter(IIRFilterSize::Size3)
        .with_gas_measurement(Duration::from_millis(1500), 320, 25)
        .with_run_gas(true)
        .build();

    // Initialize modem
    let mut wifi_driver = EspWifi::new(
        peripherals.modem,
        sys_loop,
        Some(nvs)
    ).unwrap();

    // Set WiFi credentials
    let ssid = String::<32>::from_str("SSID").unwrap();
    let password = String::<64>::from_str("PASSWORD").unwrap();

    wifi_driver.set_configuration(&Configuration::Client(ClientConfiguration{
        ssid: ssid,
        password: password,
        ..Default::default()
    })).unwrap();

    wifi_driver.start().unwrap();
    wifi_driver.connect().unwrap();

    while !wifi_driver.is_connected().unwrap(){
        let config = wifi_driver.get_configuration().unwrap();
        log::info!("Waiting for station {:?}", config);
    }

    log::info!("Should be connected now");
    
    loop {
        log::info!("IP info: {:?}", wifi_driver.sta_netif().get_ip_info().unwrap());
        sleep(Duration::new(10,0));
    }
}
