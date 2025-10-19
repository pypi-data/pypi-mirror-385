/**
 * Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
import Alpine from "alpinejs";
import { tableComponent } from "./table";
import { tablePaginedComponent } from "./table_pagined";
import { lockBoxComponent } from "./lockbox";
import { modalConfirmCallComponent, openModalConfirmCall } from "./modal";

window.tableComponent = tableComponent;
window.tablePaginedComponent = tablePaginedComponent;
window.lockBoxComponent = lockBoxComponent;
window.modalConfirmCallComponent = modalConfirmCallComponent;
window.openModalConfirmCall = openModalConfirmCall;

window.Alpine = Alpine;
Alpine.start();